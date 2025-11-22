from app.services.ocr_service import download_image_from_url, scan_receipt_with_gemini, SYSTEM_INSTRUCTION
from app.models.kapso import KapsoImage


def handle_image_message(message: KapsoImage) -> None:
    image_content, mime_type = download_image_from_url(message.link)
    ocr_result = scan_receipt_with_gemini(image_content, mime_type, SYSTEM_INSTRUCTION)
    return ocr_result
