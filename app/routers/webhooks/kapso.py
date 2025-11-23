import logging
from fastapi import APIRouter, Request, Response
from app.models.kapso import KapsoWebhookMessageReceived
from app.logic.message_receiver import (
    handle_payment_with_context,
    handle_text_message,
    handle_voice_message,
    check_existing_user_logic,
)
from app.database import db_manager

router = APIRouter(prefix="/webhooks/kapso")

logger = logging.getLogger(__name__)


@router.post("/received", status_code=200)
async def kapso_received_webhook(request: Request, payload: KapsoWebhookMessageReceived):
    async with db_manager.sessionmaker()() as db_session:
        await check_existing_user_logic(db_session, payload.conversation)
        
        if payload.message.is_image():
            # Try to get context from last message
            context_message = None
            if payload.conversation.kapso and payload.conversation.kapso.last_message_text:
                context_message = payload.conversation.kapso.last_message_text
                logger.info(f"Using context from last message: {context_message}")
            
            await handle_payment_with_context(
                db_session,
                payload.message.image,
                payload.message.sender,
                context_message=context_message,
            )
        elif payload.message.is_text():
            await handle_text_message(db_session, payload.message.text, payload.message.sender)
        elif payload.message.is_audio():
            await handle_voice_message(db_session, payload.conversation, payload.message.sender)
    return Response(status_code=200)
