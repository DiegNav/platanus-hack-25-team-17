from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from app.database.sql.session import get_all_session_debtors_from_active_session
from app.database.models.user import User
from app.database.sql.payment import get_pending_items_by_user_id
from app.integrations.kapso import send_text_message
from app.database.sql.payment_methods import get_user_payment_methods


async def build_collection_message(db_session: AsyncSession, user: User) -> str:
    """Build a collection message for a user showing all their pending debts.

    Args:
        db_session: Database session
        user: User to build the message for

    Returns:
        Formatted message string with debts grouped by invoice
    """
    # Get all pending items for this user
    items = await get_pending_items_by_user_id(db_session, user.id)

    if not items:
        return "No tienes deudas pendientes."

    # Group items by invoice
    items_by_invoice = defaultdict(list)
    for item in items:
        items_by_invoice[item.invoice].append(item)

    # Build message parts
    message_parts = []

    for invoice, invoice_items in items_by_invoice.items():
        # Calculate total from all items for this invoice
        total_from_all_items = sum(float(item.total) for item in invoice_items)

        # Get payer name
        payer_name = invoice.payer.name

        # Build the header for this invoice
        message_parts.append(f"Le debes a {payer_name} {total_from_all_items:.2f}:")

        # Build bullet list of items
        for item in invoice_items:
            item_description = item.description or "Sin descripción"
            item_total = float(item.total)
            message_parts.append(f"  • {item_description}: {item_total:.2f}")

        # Add blank line between invoices
        message_parts.append("")

    # Join all parts and remove trailing newline
    user_payment_methods = await get_user_payment_methods(db_session, user.id)
    message_parts.append("Puedes pagar a:")
    for payment_method in user_payment_methods:
        message_parts.append(f"• {payment_method.name}:\n {payment_method.description}\n")
    return "\n".join(message_parts).rstrip()


async def send_collection_message_to_all_debtors(db_session: AsyncSession, number: str) -> None:
    users = await get_all_session_debtors_from_active_session(db_session, number)
    for user in users:
        message = await build_collection_message(db_session, user)
        send_text_message(user.phone_number, message)
