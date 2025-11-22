from sqlalchemy.orm import Session
from app.database.models.user import User


def get_user_by_phone_number(db_session: Session, phone_number: str) -> User | None:
    return db_session.query(User).filter(User.phone_number == phone_number).one_or_none()


def create_user(db_session: Session, phone_number: str, name: str) -> None:
    user = User(phone_number=phone_number, name=name)
    db_session.add(user)
    db_session.commit()
