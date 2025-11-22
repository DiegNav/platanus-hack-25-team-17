import asyncio

from sqlalchemy.exc import NoResultFound
from app.services.ocr_service import download_image_from_url, scan_receipt
from app.models.kapso import KapsoImage, KapsoTextMessage
from app.models.receipt import ReceiptExtraction, TransferExtraction, ReceiptDocumentType
from app.database.sql.invoice import create_invoice_with_items
from app.integrations.kapso import send_text_message
from sqlalchemy.orm.exc import MultipleResultsFound
from app.utils.messages import TOO_MANY_ACTIVE_SESSIONS_MESSAGE, build_invoice_created_message, build_session_id_link
from app.database.sql.user import get_user_by_phone_number
from app.database.sql.payment import get_pending_items_by_user_id, process_payment
from app.services.agent.processor import process_user_command
from app.models.text_agent import ActionType
from app.database.sql.session import create_session
from sqlalchemy.orm import Session


def handle_receipt(db_session: Session, receipt: ReceiptExtraction, sender: str) -> None:
    tip = receipt.tip / receipt.total_amount
    try:
        invoice, items = create_invoice_with_items(db_session, receipt, tip, sender)
        send_text_message(sender, build_invoice_created_message(invoice, items))
        send_text_message(sender, "Para compartir la sesión de cobro con más personas, comparte el siguiente mensaje:")
        send_text_message(sender, build_session_id_link(invoice.session_id))
    except MultipleResultsFound:
        send_text_message(sender, TOO_MANY_ACTIVE_SESSIONS_MESSAGE)
        return
    except NoResultFound:
        send_text_message(sender, "No hay una sesión activa para este usuario.")
        return


def handle_transfer(db_session: Session, transfer: TransferExtraction, sender: str) -> None:
    """Handle a transfer payment from a user.
    
    This function:
    1. Gets the user by phone number (sender)
    2. Finds all pending items for the user across their sessions
    3. Matches the transfer amount with pending items
    4. Creates a payment and marks items as paid
    5. Updates invoice pending amounts
    
    Args:
        transfer: TransferExtraction with amount, recipient, description
        sender: Phone number of the user making the transfer
    """
    from app.routers.webhooks.kapso import get_sync_session
    db_session = get_sync_session()
    try:
        # Get user by phone number
        user = get_user_by_phone_number(db_session, sender)
        if not user:
            send_text_message(sender, "Usuario no encontrado. Por favor, verifica tu número de teléfono.")
            return
        
        # Get all pending items for this user
        pending_items = get_pending_items_by_user_id(db_session, user.id)
        
        if not pending_items:
            send_text_message(sender, "No tienes items pendientes de pago.")
            return
        
        # Calculate total pending amount
        total_pending = sum(float(item.total) for item in pending_items)
        transfer_amount = float(transfer.amount)
        
        # Check if transfer amount matches (with small tolerance for rounding)
        tolerance = 0.01  # 1 cent tolerance
        if abs(transfer_amount - total_pending) > tolerance:
            send_text_message(
                sender,
                f"El monto de la transferencia (${transfer_amount:.2f}) no coincide con el total pendiente (${total_pending:.2f}). "
                f"Por favor, verifica el monto."
            )
            return
        
        # Get the receiver (payer of the first invoice)
        # All items should be from invoices where the same user is the payer
        first_invoice = pending_items[0].invoice
        receiver_id = first_invoice.payer_id
        
        # Process the payment
        try:
            payment = process_payment(
                db_session=db_session,
                payer_id=user.id,
                receiver_id=receiver_id,
                amount=transfer_amount,
                items_to_pay=pending_items,
            )
            
            db_session.commit()
            send_text_message(
                sender,
                f"✅ Pago procesado exitosamente por ${transfer_amount:.2f}. "
                f"Se han marcado {len(pending_items)} item(s) como pagados."
            )
        except Exception as e:
            db_session.rollback()
            send_text_message(
                sender,
                f"❌ Error al procesar el pago: {str(e)}. Por favor, intenta nuevamente."
            )
    finally:
        db_session.close()


async def handle_image_message(image: KapsoImage, sender: str) -> None:
    """Handle an image message from Kapso.
    
    This function:
    1. Downloads the image from the URL
    2. Scans it with OCR to detect if it's a receipt or transfer
    3. Routes to the appropriate handler
    
    Args:
        image: KapsoImage with link to the image
        sender: Phone number of the user who sent the image
    """
    image_content, mime_type = await download_image_from_url(image.link)
    ocr_result = await scan_receipt(image_content, mime_type)
    if ocr_result.document_type == ReceiptDocumentType.RECEIPT:
        handle_receipt(db_session, ocr_result.receipt, sender)
    elif ocr_result.document_type == ReceiptDocumentType.TRANSFER:
        handle_transfer(db_session, ocr_result.transfer)


async def handle_text_message(db_session: Session, message: KapsoTextMessage, sender: str) -> None:
    action_to_execute = await process_user_command(message.text.body)
    if action_to_execute.action == ActionType.CREATE_SESSION:
        create_session(db_session, action_to_execute.create_session_data.description, sender)
