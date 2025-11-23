from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.payment_method import PaymentMethod
from sqlalchemy import select


async def get_user_payment_methods(db_session: AsyncSession, user_id: int) -> list[PaymentMethod]:
    result = await db_session.execute(select(PaymentMethod).where(PaymentMethod.id_user == user_id))
    return result.scalars().all()
