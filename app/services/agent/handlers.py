"""Action handlers for agent service."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent.database import (
    assign_item_to_user_in_db,
    close_session_in_db,
    create_session_in_db,
)
from app.services.agent.schemas import ActionType, AgentActionSchema
from app.database.models import Item, Session

logger = logging.getLogger(__name__)

# Type alias for action handler functions
ActionHandler = Callable[[AsyncSession, AgentActionSchema], Awaitable[Any]]


async def _handle_create_session(
    db: AsyncSession, action_schema: AgentActionSchema
) -> Session:
    """Handle CREATE_SESSION action.

    Args:
        db: Database session
        action_schema: Agent action schema with create_session_data

    Returns:
        Session: Created session

    Raises:
        ValueError: If create_session_data is None or description is missing
    """
    if not action_schema.create_session_data:
        raise ValueError("create_session_data is required for CREATE_SESSION action")

    return await create_session_in_db(
        db, description=action_schema.create_session_data.description
    )


async def _handle_close_session(
    db: AsyncSession, action_schema: AgentActionSchema
) -> Session:
    """Handle CLOSE_SESSION action.

    Args:
        db: Database session
        action_schema: Agent action schema with close_session_data

    Returns:
        Session: Found session

    Raises:
        ValueError: If close_session_data is None or session not found
    """
    if not action_schema.close_session_data:
        raise ValueError("close_session_data is required for CLOSE_SESSION action")

    data = action_schema.close_session_data
    return await close_session_in_db(
        db, session_id=data.session_id, session_description=data.session_description
    )


async def _handle_assign_item_to_user(
    db: AsyncSession, action_schema: AgentActionSchema
) -> Item:
    """Handle ASSIGN_ITEM_TO_USER action.

    Args:
        db: Database session
        action_schema: Agent action schema with assign_item_to_user_data

    Returns:
        Item: Updated item

    Raises:
        ValueError: If assign_item_to_user_data is None or required fields are missing
    """
    if not action_schema.assign_item_to_user_data:
        raise ValueError(
            "assign_item_to_user_data is required for ASSIGN_ITEM_TO_USER action"
        )

    data = action_schema.assign_item_to_user_data
    return await assign_item_to_user_in_db(
        db,
        item_id=data.item_id,
        user_id=data.user_id,
        user_name=data.user_name,
        invoice_id=data.invoice_id,
        item_description=data.item_description,
    )


async def _handle_unknown(
    db: AsyncSession, action_schema: AgentActionSchema
) -> dict[str, str]:
    """Handle UNKNOWN action.

    This handler is called when the agent cannot determine a valid action
    from the user's text. It returns a message indicating that the action
    could not be determined.

    Args:
        db: Database session (not used, but required for handler signature)
        action_schema: Agent action schema with unknown_data

    Returns:
        dict: Message indicating unknown action
    """
    reason = (
        action_schema.unknown_data.reason
        if action_schema.unknown_data
        else "No se pudo determinar la acción a partir del texto"
    )
    suggested = (
        action_schema.unknown_data.suggested_action
        if action_schema.unknown_data
        else None
    )

    message = f"Acción desconocida: {reason}"
    if suggested:
        message += f". Sugerencia: {suggested}"

    logger.warning(f"Unknown action detected: {reason}")

    return {"message": message, "reason": reason, "suggested_action": suggested}


# Mapping between ActionType and their corresponding handler functions
ACTION_HANDLERS: dict[ActionType, ActionHandler] = {
    ActionType.CREATE_SESSION: _handle_create_session,
    ActionType.CLOSE_SESSION: _handle_close_session,
    ActionType.ASSIGN_ITEM_TO_USER: _handle_assign_item_to_user,
    ActionType.UNKNOWN: _handle_unknown,
}

