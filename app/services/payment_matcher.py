"""Service for matching payment intents with database items."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.models.payment_matching import (
    PaymentIntent,
    ItemPaymentMatch,
    PaymentMatchResult,
)
from app.database.models.item import Item
from app.database.models.invoice import Invoice
from app.database.sql.session import get_active_session_by_user_id
from app.database.sql.user import get_user_by_phone_number
from app.config.settings import settings

logger = logging.getLogger(__name__)


class ItemMatchChoice(BaseModel):
    """Schema for item matching output."""
    
    intent_description: str = Field(..., description="Original description from user intent")
    matched_item_id: int | None = Field(
        ..., 
        description="ID of the matched database item, or None if no good match"
    )
    match_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence of the match (0.0 to 1.0)"
    )
    reasoning: str = Field(..., description="Reasoning for the match decision")


class ItemMatchingResult(BaseModel):
    """Result of matching multiple items."""
    
    matches: list[ItemMatchChoice] = Field(..., description="List of matched items")


ITEM_MATCHING_SYSTEM_PROMPT = """Eres un experto en hacer matching semántico entre descripciones de items en español.

Tu tarea es encontrar el mejor match entre:
1. Lo que el usuario dice que pagó (intent_description)
2. Los items disponibles en la base de datos (database_items)

Reglas:
- Busca similitud semántica (ej: "bebida" puede matchear con "Coca Cola", "Sprite", etc.)
- "pizza" debe matchear con items que contengan "pizza"
- "hamburguesa" con items que digan "hamburguesa" o "burger"
- Si hay múltiples opciones similares, escoge la primera disponible (is_paid=false)
- Si NO hay un buen match, devuelve matched_item_id como None
- Usa match_confidence para indicar qué tan seguro estás (1.0 = muy seguro, < 0.5 = poco seguro)

Considera sinónimos y variaciones:
- bebida, gaseosa, refresco → Coca Cola, Sprite, Fanta, Pepsi
- cerveza, chela → Cerveza, Beer
- papas, patatas → Papas Fritas, French Fries
- postre, dulce → cualquier postre
"""


class PaymentMatcherService:
    """Service for matching payment intents with database items."""
    
    def __init__(self):
        """Initialize the payment matcher service."""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=settings.OPENAI_API_KEY,
        )
        
        self.structured_llm = self.llm.with_structured_output(ItemMatchingResult)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", ITEM_MATCHING_SYSTEM_PROMPT),
            ("user", """Items del usuario (intents):
{user_intents}

Items disponibles en la base de datos:
{database_items}

Haz el matching y devuelve el resultado.""")
        ])
        
        self.chain = self.prompt | self.structured_llm
    
    async def get_session_unpaid_items(
        self, 
        db_session: AsyncSession, 
        user_phone: str
    ) -> list[Item]:
        """Get all unpaid items from the user's active session.
        
        Args:
            db_session: Database session
            user_phone: User's phone number
            
        Returns:
            List of unpaid items
        """
        user = await get_user_by_phone_number(db_session, user_phone)
        if not user:
            return []
        
        session = await get_active_session_by_user_id(db_session, user.id)
        if not session:
            return []
        
        # Get all unpaid items from invoices in this session
        result = await db_session.execute(
            select(Item)
            .join(Invoice, Item.invoice_id == Invoice.id)
            .where(Invoice.session_id == session.id)
            .where(Item.is_paid == False)
            .order_by(Item.id)
        )
        
        items = result.scalars().all()
        return list(items)
    
    async def match_items(
        self,
        payment_intent: PaymentIntent,
        available_items: list[Item],
    ) -> ItemMatchingResult:
        """Match payment intent items with database items using LLM.
        
        Args:
            payment_intent: Payment intent with user's claimed items
            available_items: Available items from database
            
        Returns:
            ItemMatchingResult with matched items
        """
        if not payment_intent.items_paid:
            return ItemMatchingResult(matches=[])
        
        # Format user intents
        user_intents = "\n".join([
            f"- {item.item_description} (cantidad: {item.quantity})"
            for item in payment_intent.items_paid
        ])
        
        # Format database items
        database_items = "\n".join([
            f"- ID: {item.id}, Descripción: '{item.description}', "
            f"Precio: ${item.unit_price:.2f}, Total: ${item.total:.2f}, "
            f"Pagado: {item.is_paid}"
            for item in available_items
        ])
        
        if not database_items:
            logger.warning("No available items in database to match")
            return ItemMatchingResult(matches=[])
        
        logger.info(f"Matching {len(payment_intent.items_paid)} intent items "
                   f"with {len(available_items)} database items")
        
        try:
            result = await self.chain.ainvoke({
                "user_intents": user_intents,
                "database_items": database_items,
            })
            logger.info(f"Matching result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error matching items: {e}")
            return ItemMatchingResult(matches=[])
    
    async def create_payment_match_result(
        self,
        db_session: AsyncSession,
        matching_result: ItemMatchingResult,
        payment_amount: float,
    ) -> PaymentMatchResult:
        """Create a complete payment match result.
        
        Args:
            db_session: Database session
            matching_result: Item matching result from LLM
            payment_amount: Actual payment amount from transfer
            
        Returns:
            PaymentMatchResult with complete analysis
        """
        matched_items: list[ItemPaymentMatch] = []
        expected_amount = 0.0
        
        for match in matching_result.matches:
            if match.matched_item_id is None or match.match_confidence < 0.5:
                logger.warning(f"Skipping low confidence match: {match}")
                continue
            
            # Get item from database
            result = await db_session.execute(
                select(Item).where(Item.id == match.matched_item_id)
            )
            item = result.scalar_one_or_none()
            
            if not item:
                logger.warning(f"Item {match.matched_item_id} not found in database")
                continue
            
            matched_items.append(ItemPaymentMatch(
                item_id=item.id,
                description=item.description,
                unit_price=float(item.unit_price),
                total_price=float(item.total),
                matched_from_intent=match.intent_description,
            ))
            
            expected_amount += float(item.total)
        
        difference = payment_amount - expected_amount
        
        if abs(difference) < 0.01:  # Practically equal (accounting for floating point)
            payment_status = "exact"
        elif difference > 0:
            payment_status = "overpaid"
        else:
            payment_status = "underpaid"
        
        return PaymentMatchResult(
            matched_items=matched_items,
            expected_amount=expected_amount,
            actual_amount=payment_amount,
            difference=difference,
            payment_status=payment_status,
        )


# Global instance
payment_matcher = PaymentMatcherService()


async def match_payment_to_items(
    db_session: AsyncSession,
    user_phone: str,
    payment_intent: PaymentIntent,
    payment_amount: float,
) -> PaymentMatchResult:
    """Main function to match a payment to items.
    
    Args:
        db_session: Database session
        user_phone: User's phone number
        payment_intent: Extracted payment intent
        payment_amount: Actual payment amount
        
    Returns:
        PaymentMatchResult with complete matching and analysis
    """
    # Get available items
    available_items = await payment_matcher.get_session_unpaid_items(
        db_session, user_phone
    )
    
    if not available_items:
        logger.warning(f"No unpaid items found for user {user_phone}")
        return PaymentMatchResult(
            matched_items=[],
            expected_amount=0.0,
            actual_amount=payment_amount,
            difference=payment_amount,
            payment_status="overpaid" if payment_amount > 0 else "exact",
        )
    
    # Match items using LLM
    matching_result = await payment_matcher.match_items(
        payment_intent, available_items
    )
    
    # Create final result
    return await payment_matcher.create_payment_match_result(
        db_session, matching_result, payment_amount
    )

