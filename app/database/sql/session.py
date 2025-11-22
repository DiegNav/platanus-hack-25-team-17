from sqlalchemy.orm import Session
from app.database.models.session import Session, SessionStatus
from app.database.sql.user import get_user_by_phone_number


def get_active_session_by_user_id(db_session: Session, user_id: int) -> Session | None:
    return (
        db_session.query(Session)
        .filter(Session.owner_id == user_id)
        .filter(Session.status == SessionStatus.ACTIVE)
        .one()
    )


def create_session(db_session: Session, description: str, owner_number: str) -> Session:
    user = get_user_by_phone_number(db_session, owner_number)
    session = Session(description=description, owner_id=user.id, status=SessionStatus.ACTIVE)
    db_session.add(session)
    db_session.commit()
    return session
