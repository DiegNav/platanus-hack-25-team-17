from fastapi import APIRouter, Request
from app.models.kapso import KapsoWebhookMessageReceived
from app.logic.message_receiver import handle_image_message, handle_text_message
from app.database import db_manager

router = APIRouter()

router.prefix("/webhooks/kapso")


@router.post("/received", status_code=200)
def kapso_webhook(request: Request, payload: KapsoWebhookMessageReceived):
    db_session = db_manager.db_session()
    if payload.message.is_image():
        handle_image_message(db_session, payload.message.image, payload.message.sender)
    elif payload.message.is_text():
        handle_text_message(db_session, payload.message.text, payload.message.sender)
