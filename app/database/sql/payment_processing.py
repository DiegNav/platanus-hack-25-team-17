"""Payment processing logic for marking items as paid."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.payment_matching import PaymentMatchResult
from app.database.models.item import Item
from app.database.models.invoice import Invoice
from app.database.models.payment import Payment
from app.database.sql.user import get_user_by_phone_number

logger = logging.getLogger(__name__)


async def process_payment_result(
    db_session: AsyncSession,
    payment_match: PaymentMatchResult,
    user_phone: str,
    payment_description: str = "Pago de items",
) -> tuple[list[Item], Item | None]:
    """Process a payment match result and update the database.
    
    This function handles the payment logic:
    - If paid exact or more: mark items as paid, ignore extra
    - If paid less: mark items as paid, create a "resto faltante" item
    
    Args:
        db_session: Database session
        payment_match: Payment match result with items and amounts
        user_phone: User's phone number
        payment_description: Description for the payment record
        
    Returns:
        Tuple of (paid_items, remainder_item)
        - paid_items: List of items that were marked as paid
        - remainder_item: New "resto faltante" item if underpaid, None otherwise
    """
    user = await get_user_by_phone_number(db_session, user_phone)
    if not user:
        raise ValueError(f"User with phone {user_phone} not found")
    
    if not payment_match.matched_items:
        logger.warning("No matched items to process payment for")
        return [], None
    
    paid_items: list[Item] = []
    remainder_item: Item | None = None
    
    # Get the invoice_id from the first matched item (all should be from same session)
    first_item_result = await db_session.execute(
        select(Item).where(Item.id == payment_match.matched_items[0].item_id)
    )
    first_item = first_item_result.scalar_one()
    invoice_id = first_item.invoice_id
    
    # Get the invoice to find the receiver (payer of the original receipt)
    invoice_result = await db_session.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = invoice_result.scalar_one()
    receiver_id = invoice.payer_id
    
    # Create a payment record
    payment = Payment(
        amount=payment_match.actual_amount,
        payer_id=user.id,
        receiver_id=receiver_id,
    )
    db_session.add(payment)
    await db_session.flush()  # Get payment ID
    
    # Mark all matched items as paid
    for matched_item in payment_match.matched_items:
        result = await db_session.execute(
            select(Item).where(Item.id == matched_item.item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            logger.warning(f"Item {matched_item.item_id} not found, skipping")
            continue
        
        if item.is_paid:
            logger.warning(f"Item {item.id} already paid, skipping")
            continue
        
        # Mark as paid
        item.is_paid = True
        item.paid_amount = item.total
        item.debtor_id = user.id
        item.payment_id = payment.id
        
        paid_items.append(item)
        logger.info(f"Marked item {item.id} ({item.description}) as paid")
    
    # Handle underpayment: create "resto faltante" item
    if payment_match.payment_status == "underpaid":
        remainder_amount = abs(payment_match.difference)
        
        logger.info(f"Creating 'resto faltante' item for ${remainder_amount:.2f}")
        
        remainder_item = Item(
            description=f"Resto faltante del pago",
            invoice_id=invoice_id,
            debtor_id=user.id,
            unit_price=remainder_amount,
            paid_amount=0.0,
            tip=0.0,
            total=remainder_amount,
            is_paid=False,
            payment_id=None,
        )
        db_session.add(remainder_item)
        logger.info(f"Created remainder item: ${remainder_amount:.2f}")
    
    elif payment_match.payment_status == "overpaid":
        logger.info(
            f"User overpaid by ${payment_match.difference:.2f}. "
            "Extra amount will be ignored."
        )
    
    else:  # exact
        logger.info("Payment amount matches expected amount exactly")
    
    # Update invoice pending_amount (invoice already fetched above)
    # Recalculate pending amount based on all unpaid items
    unpaid_items_result = await db_session.execute(
        select(Item)
        .where(Item.invoice_id == invoice_id)
        .where(Item.is_paid == False)
    )
    unpaid_items = unpaid_items_result.scalars().all()
    
    invoice.pending_amount = sum(float(item.total) for item in unpaid_items)
    
    await db_session.commit()
    await db_session.refresh(payment)
    
    for item in paid_items:
        await db_session.refresh(item)
    
    if remainder_item:
        await db_session.refresh(remainder_item)
    
    return paid_items, remainder_item


async def get_payment_summary(
    db_session: AsyncSession,
    paid_items: list[Item],
    remainder_item: Item | None,
) -> str:
    """Generate a human-readable payment summary message.
    
    Args:
        db_session: Database session
        paid_items: List of items that were marked as paid
        remainder_item: Remainder item if underpaid
        
    Returns:
        Formatted summary message for WhatsApp
    """
    if not paid_items:
        return "❌ No se pudo procesar el pago. No se encontraron items que coincidan."
    
    summary_lines = ["✅ Pago procesado exitosamente\n"]
    summary_lines.append("Items pagados:")
    
    total_paid = 0.0
    for item in paid_items:
        summary_lines.append(f"• {item.description}: ${float(item.total):.2f}")
        total_paid += float(item.total)
    
    summary_lines.append(f"\nTotal: ${total_paid:.2f}")
    
    if remainder_item:
        summary_lines.append(
            f"\n⚠️ Pago insuficiente. "
            f"Se creó un item por el resto faltante: ${float(remainder_item.total):.2f}"
        )
        summary_lines.append(
            "Por favor, completa el pago del resto faltante."
        )
    
    return "\n".join(summary_lines)

