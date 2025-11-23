"""Payment matching agent using LangChain and OpenAI structured outputs."""

import logging
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.models.payment_matching import PaymentIntent, ItemMatch
from app.config.settings import settings

logger = logging.getLogger(__name__)


# System prompt for payment intent extraction
PAYMENT_INTENT_SYSTEM_PROMPT = """Eres un asistente experto en extraer intenciones de pago de mensajes de WhatsApp en español.

Tu tarea es analizar el mensaje del usuario y extraer:
1. Los items que el usuario dice haber pagado
2. La cantidad de cada item
3. Si realmente es una intención de pago

Los usuarios pueden decir cosas como:
- "pagué una bebida y una pizza"
- "pago 2 hamburguesas"
- "ya pagué mi parte: coca cola y papas"
- "transferí por la cerveza"

Instrucciones:
- Extrae todos los items mencionados
- Si no mencionan cantidad, asume 1
- Si el mensaje NO es sobre un pago, marca is_payment como false
- Normaliza las descripciones (ej: "bebida", "coca" -> "bebida")
- Sé tolerante con errores de tipeo

Ejemplos de items comunes: bebida, pizza, hamburguesa, papas, ensalada, postre, café, cerveza, agua, etc.
"""


class PaymentIntentAgent:
    """Agent for extracting payment intent from user messages."""
    
    def __init__(self):
        """Initialize the payment intent agent."""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=settings.OPENAI_API_KEY,
        )
        
        # Create structured output LLM
        self.structured_llm = self.llm.with_structured_output(PaymentIntent)
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", PAYMENT_INTENT_SYSTEM_PROMPT),
            ("user", "Mensaje del usuario: {user_message}\n\nExtrae la intención de pago.")
        ])
        
        # Create chain
        self.chain = self.prompt | self.structured_llm
    
    async def extract_payment_intent(self, user_message: str) -> PaymentIntent:
        """Extract payment intent from user message.
        
        Args:
            user_message: The user's WhatsApp message
            
        Returns:
            PaymentIntent with extracted items and metadata
        """
        logger.info(f"Extracting payment intent from message: {user_message}")
        
        try:
            result = await self.chain.ainvoke({"user_message": user_message})
            logger.info(f"Extracted payment intent: {result}")
            return result
        except Exception as e:
            logger.error(f"Error extracting payment intent: {e}")
            # Return default empty intent on error
            return PaymentIntent(
                items_paid=[],
                is_payment=False,
                payment_description=f"Error: {str(e)}"
            )


# Global instance
payment_agent = PaymentIntentAgent()


async def extract_payment_intent_from_message(message: str) -> PaymentIntent:
    """Extract payment intent from a message.
    
    Args:
        message: User's message describing what they paid for
        
    Returns:
        PaymentIntent with extracted information
    """
    return await payment_agent.extract_payment_intent(message)

