"""OCR service for receipt extraction using Google Gemini 2.5 Flash."""

import json
import logging
from typing import Any

import google.generativeai as genai
import httpx

from app.config import settings
from app.models.receipt import DocumentExtraction, ReceiptExtraction, TransferExtraction

logger = logging.getLogger(__name__)

# System instruction for Gemini
SYSTEM_INSTRUCTION = """Eres un motor OCR especializado en documentos financieros. Tu tarea es identificar el tipo de documento y extraer datos estructurados.

PRIMERO: Identifica si el documento es una BOLETA/RECIBO de restaurante o una TRANSFERENCIA bancaria.

Si es una BOLETA/RECIBO:
- Busca explícitamente campos de 'Propina', 'Tip' o 'Servicio'.
- Devuelve un JSON con: "document_type": "receipt", y los campos: "merchant", "date", "total_amount", "tip", "items".
- "items": [{"description": "descripción del ítem", "amount": 0.0, "count": 1}]
- Si la propina no aparece explícitamente, el valor es 0.

Si es una TRANSFERENCIA:
- Devuelve un JSON con: "document_type": "transfer", y los campos: "recipient", "amount", "description".
- "recipient": nombre del destinatario o identificador de cuenta.
- "amount": monto de la transferencia.
- "description": descripción o referencia de la transferencia (puede ser null si no existe).

No uses bloques de código markdown. Devuelve el JSON crudo.

Formato esperado para BOLETA:
{
  "document_type": "receipt",
  "merchant": "nombre del comercio",
  "date": "YYYY-MM-DD",
  "total_amount": 0.0,
  "tip": 0.0,
  "items": [
    {"description": "descripción del ítem", "amount": 0.0}
  ]
}

Formato esperado para TRANSFERENCIA:
{
  "document_type": "transfer",
  "recipient": "nombre del destinatario",
  "amount": 0.0,
  "description": "descripción o referencia (puede ser null)"
}"""


def _parse_gemini_response(response_text: str) -> dict[str, Any]:
    """Parse Gemini response and extract JSON.

    Handles cases where Gemini includes explanatory text before/after the JSON,
    or wraps JSON in markdown code blocks.

    Args:
        response_text: Raw response text from Gemini

    Returns:
        dict: Parsed JSON data

    Raises:
        ValueError: If JSON cannot be parsed
    """
    import re

    text = response_text.strip()

    # First, try to find JSON inside markdown code blocks (```json ... ``` or ``` ... ```)
    json_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    json_match = re.search(json_block_pattern, text, re.DOTALL)
    if json_match:
        text = json_match.group(1).strip()
    else:
        # Try to find JSON object by finding balanced braces
        # Find the first { and then find the matching }
        first_brace = text.find("{")
        if first_brace != -1:
            # Count braces to find the matching closing brace
            brace_count = 0
            for i in range(first_brace, len(text)):
                if text[i] == "{":
                    brace_count += 1
                elif text[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        # Found the matching closing brace
                        text = text[first_brace : i + 1]
                        break
        else:
            # Fallback: try to parse the whole text after removing markdown
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        logger.error(f"Response text: {response_text[:500]}")
        raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")


async def download_image_from_url(image_url: str) -> tuple[bytes, str]:
    """Download image from URL and return content with MIME type.

    Args:
        image_url: URL of the image to download

    Returns:
        tuple: (image_content, mime_type)

    Raises:
        ValueError: If URL is invalid, download fails, or file is not an image
        RuntimeError: If HTTP request fails
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"Downloading image from URL: {image_url}")
            response = await client.get(image_url)
            response.raise_for_status()

            # Get content type from headers or guess from URL
            content_type = response.headers.get("content-type", "")
            if content_type:
                mime_type = content_type.split(";")[0].strip()
            else:
                # Try to guess from URL extension
                if image_url.lower().endswith((".jpg", ".jpeg")):
                    mime_type = "image/jpeg"
                elif image_url.lower().endswith(".png"):
                    mime_type = "image/png"
                elif image_url.lower().endswith(".webp"):
                    mime_type = "image/webp"
                elif image_url.lower().endswith(".gif"):
                    mime_type = "image/gif"
                else:
                    mime_type = "image/jpeg"  # Default

            # Validate it's an image
            if not mime_type.startswith("image/"):
                raise ValueError(f"URL does not point to an image. Content-Type: {mime_type}")

            image_content = response.content
            if not image_content:
                raise ValueError("Downloaded image is empty")

            logger.info(f"Successfully downloaded image: {len(image_content)} bytes, type: {mime_type}")
            return image_content, mime_type

    except httpx.HTTPError as e:
        logger.error(f"HTTP error downloading image: {str(e)}")
        raise RuntimeError(f"Failed to download image from URL: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error downloading image: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to download image: {str(e)}") from e


async def scan_receipt_with_gemini(
    file_content: bytes, mime_type: str, custom_prompt: str | None = None
) -> DocumentExtraction:
    """Scan document image using Google Gemini 2.5 Flash OCR.

    Detects if the document is a receipt or transfer and extracts data accordingly.

    Args:
        file_content: Binary content of the image file
        mime_type: MIME type of the image (e.g., 'image/jpeg', 'image/png')
        custom_prompt: Optional custom prompt/instruction for Gemini. If None, uses default.

    Returns:
        DocumentExtraction: Validated document data (receipt or transfer)

    Raises:
        ValueError: If API key is missing, API call fails, or response is invalid
        RuntimeError: If Gemini API returns an error
    """
    # Validate API key
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured in environment variables")

    try:
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Use custom prompt if provided, otherwise use default
        system_instruction = custom_prompt if custom_prompt else SYSTEM_INSTRUCTION

        # Initialize model with system instruction
        # Using gemini-2.5-flash as specified
        # If model is not available, try gemini-2.0-flash-exp or gemini-1.5-flash
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=system_instruction,
            )
        except Exception:
            # Fallback to available model if 2.5-flash doesn't exist yet
            logger.warning("gemini-2.5-flash not available, using gemini-2.0-flash-exp")
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                system_instruction=system_instruction,
            )

        # Prepare image part
        image_part = {
            "mime_type": mime_type,
            "data": file_content,
        }

        # Generate content
        logger.info("Sending image to Gemini for OCR extraction")
        response = model.generate_content(
            contents=[image_part],
            generation_config={
                "temperature": 0.1,  # Low temperature for consistent extraction
                "max_output_tokens": 2048,
            },
        )

        # Extract response text
        if not response.text:
            raise ValueError("Empty response from Gemini API")

        logger.info("Received response from Gemini, parsing JSON")
        response_data = _parse_gemini_response(response.text)

        # Validate document type
        document_type = response_data.get("document_type", "").lower()
        if document_type not in ["receipt", "transfer"]:
            raise ValueError(f"Invalid document_type: {document_type}. Must be 'receipt' or 'transfer'")

        # Create DocumentExtraction based on type
        if document_type == "receipt":
            receipt_data = ReceiptExtraction(**response_data)
            document_extraction = DocumentExtraction(
                document_type="receipt",
                receipt=receipt_data,
                transfer=None,
            )
            logger.info(
                f"Successfully extracted receipt: {receipt_data.merchant}, "
                f"Total: ${receipt_data.total_amount}, Tip: ${receipt_data.tip}"
            )
        else:  # transfer
            transfer_data = TransferExtraction(**response_data)
            document_extraction = DocumentExtraction(
                document_type="transfer",
                receipt=None,
                transfer=transfer_data,
            )
            logger.info(
                f"Successfully extracted transfer: Recipient={transfer_data.recipient}, Amount=${transfer_data.amount}"
            )

        return document_extraction

    except ValueError as e:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to process receipt with Gemini: {str(e)}") from e
