from sqlalchemy.orm import Session
from app.database.models.session import Session, SessionStatus, session_users


def get_active_session_by_user_id(db_session: Session, user_id: int) -> Session | None:
    return (
        db_session.query(Session)
        .filter(Session.owner_id == user_id)
        .filter(Session.status == SessionStatus.ACTIVE)
        .one()
    )


def get_sessions_by_user_id(db_session: Session, user_id: int) -> list[Session]:
    """Get all sessions where a user is involved (as owner or participant).
    
    Args:
        db_session: Database session
        user_id: ID of the user
        
    Returns:
        List of sessions where the user is involved
    """
    return (
        db_session.query(Session)
        .join(session_users, Session.id == session_users.c.session_id)
        .filter(session_users.c.user_id == user_id)
        .filter(Session.status == SessionStatus.ACTIVE)
        .all()
    )
