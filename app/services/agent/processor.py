"""Agent command processor."""

import logging

from langchain_core.messages import HumanMessage

from app.services.agent.models import initialize_openai_model
from app.services.agent.prompt import get_agent_prompt
from app.models.text_agent import AgentActionSchema

logger = logging.getLogger(__name__)


async def process_user_command(user_text: str) -> AgentActionSchema:
    """Process user command in natural language and determine action to take.

    Uses OpenAI with structured outputs to classify the intent and extract
    necessary data for the action.

    Args:
        user_text: User's command in natural language

    Returns:
        AgentActionSchema: Action decision with extracted data

    Raises:
        ValueError: If API key is missing or response is invalid
        RuntimeError: If OpenAI API returns an error
    """
    try:
        # Initialize model
        model = initialize_openai_model()

        # Get structured prompt
        prompt = get_agent_prompt()

        # Create message with user text
        message = HumanMessage(content=f"{prompt}\n\nTEXTO DEL USUARIO:\n{user_text}")

        logger.info(f"Processing user command: {user_text[:100]}...")

        # Configure model with structured output
        structured_model = model.with_structured_output(AgentActionSchema)
        result = await structured_model.ainvoke([message])

        logger.info(
            f"Agent decision: action={result.action.value}, "
            f"has_create_session_data={result.create_session_data is not None}, "
            f"has_close_session_data={result.close_session_data is not None}, "
            f"has_assign_item_to_user_data={result.assign_item_to_user_data is not None}"
        )

        return result

    except ValueError as e:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Error calling OpenAI API via LangChain: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to process command with OpenAI: {str(e)}") from e
