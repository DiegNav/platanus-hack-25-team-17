"""API dependencies for dependency injection."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db_manager


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Get database session dependency.

    Yields:
        AsyncSession: Database session for the request

    Example:
        ```python
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
        ```
    """
    session_maker = db_manager.sessionmaker()
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
