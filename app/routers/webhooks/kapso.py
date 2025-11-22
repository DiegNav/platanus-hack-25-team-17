from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from app.models.kapso import KapsoWebhookMessageReceived
from app.logic.message_receiver import handle_image_message, handle_text_message
from app.database import db_manager
from app.config import settings

router = APIRouter(prefix="/webhooks/kapso")


def get_sync_session() -> Session:
    """Get a synchronous database session."""
    # Convert async database URL to sync
    db_url = settings.DATABASE_URL
    if hasattr(db_url, "unicode_string"):
        sync_url = db_url.unicode_string()
    else:
        sync_url = str(db_url)
    
    # Remove async driver if present
    sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://")
    
    engine = create_engine(sync_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


@router.post("/received", status_code=200)
def kapso_webhook(request: Request, payload: KapsoWebhookMessageReceived):
    db_session = db_manager.db_session()
    if payload.message.is_image():
        handle_image_message(db_session, payload.message.image, payload.message.sender)
    elif payload.message.is_text():
        handle_text_message(db_session, payload.message.text, payload.message.sender)
