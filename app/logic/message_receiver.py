import asyncio

from sqlalchemy.exc import NoResultFound
from app.services.ocr_service import download_image_from_url, scan_receipt
from app.models.kapso import KapsoImage
from app.models.receipt import ReceiptExtraction, TransferExtraction, ReceiptDocumentType
from app.database.sql.invoice import create_invoice_with_items
from app.integrations.kapso import send_text_message
from sqlalchemy.orm.exc import MultipleResultsFound
from app.utils.messages import TOO_MANY_ACTIVE_SESSIONS_MESSAGE, build_invoice_created_message, build_session_id_link
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


def handle_transfer(transfer: TransferExtraction) -> None:
    pass


async def handle_image_message(db_session: Session, message: KapsoImage, sender: str) -> None:
    image_content, mime_type = await download_image_from_url(message.link)
    ocr_result = await scan_receipt(image_content, mime_type)
    if ocr_result.document_type == ReceiptDocumentType.RECEIPT:
        handle_receipt(db_session, ocr_result.receipt, sender)
    elif ocr_result.document_type == ReceiptDocumentType.TRANSFER:
        handle_transfer(ocr_result.transfer)
