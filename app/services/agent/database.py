"""Database operations for agent actions."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Item, Session, User

logger = logging.getLogger(__name__)


async def create_session_in_db(db: AsyncSession, description: str) -> Session:
    """Create a new session in the database.

    Args:
        db: Database session
        description: Description of the session

    Returns:
        Session: Created session instance

    Raises:
        ValueError: If description is empty
    """
    if not description or not description.strip():
        raise ValueError("Session description cannot be empty")

    session_data = {"description": description.strip()}
    db_session = Session(**session_data)
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)

    logger.info(f"Created session with ID {db_session.id}: {description}")
    return db_session


async def close_session_in_db(
    db: AsyncSession, session_id: int | None = None, session_description: str | None = None
) -> Session:
    """Find and return a session by ID or description.

    Args:
        db: Database session
        session_id: ID of the session to find
        session_description: Description to search for (partial match)

    Returns:
        Session: Found session instance

    Raises:
        ValueError: If neither session_id nor session_description is provided
        ValueError: If session is not found
    """
    if not session_id and not session_description:
        raise ValueError("Either session_id or session_description must be provided")

    if session_id:
        result = await db.execute(select(Session).where(Session.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session with ID {session_id} not found")
        logger.info(f"Found session by ID: {session_id}")
        return session

    # Search by description (case-insensitive partial match)
    if session_description:
        result = await db.execute(select(Session).where(Session.description.ilike(f"%{session_description}%")))
        sessions = result.scalars().all()
        if not sessions:
            raise ValueError(f"Session with description containing '{session_description}' not found")
        if len(sessions) > 1:
            logger.warning(
                f"Multiple sessions found for description '{session_description}'. "
                f"Returning first match (ID: {sessions[0].id})"
            )
        logger.info(f"Found session by description: {session_description} (ID: {sessions[0].id})")
        return sessions[0]

    raise ValueError("Unable to find session")


async def assign_item_to_user_in_db(
    db: AsyncSession,
    item_id: int | None = None,
    user_id: int | None = None,
    user_name: str | None = None,
    invoice_id: int | None = None,
    item_description: str | None = None,
) -> Item:
    """Assign an item to a user by updating the item's debtor_id.

    Args:
        db: Database session
        item_id: ID of the item to assign
        user_id: ID of the user to assign to
        user_name: Name of the user to assign to
        invoice_id: ID of the invoice (used when searching by item_description)
        item_description: Description of the item (used when item_id is not provided)

    Returns:
        Item: Updated item instance

    Raises:
        ValueError: If item cannot be found or identified
        ValueError: If user cannot be found or identified
        ValueError: If neither user_id nor user_name is provided
    """
    # Find the user
    user: User | None = None
    if user_id:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
    elif user_name:
        result = await db.execute(select(User).where(User.name.ilike(f"%{user_name}%")))
        users = result.scalars().all()
        if not users:
            raise ValueError(f"User with name containing '{user_name}' not found")
        if len(users) > 1:
            logger.warning(
                f"Multiple users found for name '{user_name}'. "
                f"Using first match (ID: {users[0].id}, Name: {users[0].name})"
            )
        user = users[0]
    else:
        raise ValueError("Either user_id or user_name must be provided")

    # Find the item
    item: Item | None = None
    if item_id:
        result = await db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError(f"Item with ID {item_id} not found")
    elif item_description:
        # Note: Item model doesn't have a description field
        # We can only search by invoice_id and hope there's a single item
        # or the user must provide item_id
        if invoice_id:
            result = await db.execute(select(Item).where(Item.invoice_id == invoice_id))
            items = result.scalars().all()
            if not items:
                raise ValueError(
                    f"No items found in invoice {invoice_id}. "
                    f"Cannot match by description '{item_description}' as Item model has no description field."
                )
            # If there's only one item in the invoice, we can use it
            if len(items) == 1:
                item = items[0]
                logger.warning(
                    f"Using single item from invoice {invoice_id} for description '{item_description}'. "
                    f"Item ID: {item.id}"
                )
            else:
                raise ValueError(
                    f"Multiple items ({len(items)}) found in invoice {invoice_id}. "
                    f"Cannot match by description '{item_description}' as Item model has no description field. "
                    f"Please specify item_id to identify the exact item."
                )
        else:
            raise ValueError(
                "Item model does not have a description field. "
                "Please provide item_id to identify the item, or provide invoice_id "
                "if the invoice has only one item."
            )
    else:
        raise ValueError("Either item_id or (item_description + invoice_id) must be provided")

    # Update the item's debtor_id
    item.debtor_id = user.id
    db.add(item)
    await db.commit()
    await db.refresh(item)

    logger.info(
        f"Assigned item {item.id} to user {user.id} ({user.name}). "
        f"Previous debtor_id: {item.debtor_id if hasattr(item, '_previous_debtor_id') else 'N/A'}"
    )

    return item
