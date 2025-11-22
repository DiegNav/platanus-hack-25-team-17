from sqlalchemy.orm import Session
from app.database.models.user import User
import logging


def get_user_by_phone_number(db_session: Session, phone_number: str) -> User | None:
    logging.info(f"Getting user by phone number: {phone_number}")
    try:
        user = db_session.query(User).filter(User.phone_number == phone_number).one_or_none()
        logging.info(f"User: {user}")
        return user
    except Exception as e:
        logging.info(f"Error getting user by phone number: {e}")
        return None


def create_user(db_session: Session, phone_number: str, name: str) -> None:
    user = User(phone_number=phone_number, name=name)
    db_session.add(user)
    db_session.commit()
