from fastapi import APIRouter, Request
from app.models.kapso import KapsoWebhookMessageReceived
from app.logic.message_receiver import handle_image_message

router = APIRouter()

router.prefix("/webhooks/kapso")


@router.post("/received", status_code=200)
async def kapso_webhook(request: Request, payload: KapsoWebhookMessageReceived):
    if payload.message.is_image():
        handle_image_message(payload.message.image)
    elif payload.message.is_text():
        pass
