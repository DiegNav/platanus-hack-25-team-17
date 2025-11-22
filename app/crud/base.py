"""Generic CRUD operations base class."""

from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase[ModelType: Base, CreateSchemaType: BaseModel, UpdateSchemaType: BaseModel]:
    """Generic CRUD operations.

    Provides standard create, read, update, delete operations for any model.

    Attributes:
        model: SQLAlchemy model class
    """

    def __init__(self, model: type[ModelType]):
        """Initialize CRUD object with model.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Get a single record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            ModelType | None: Record if found, None otherwise
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            list[ModelType]: List of records
        """
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record.

        Args:
            db: Database session
            obj_in: Pydantic schema with data to create

        Returns:
            ModelType: Created record
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Update a record.

        Args:
            db: Database session
            db_obj: Database object to update
            obj_in: Pydantic schema or dict with data to update

        Returns:
            ModelType: Updated record
        """
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int) -> ModelType | None:
        """Delete a record by ID.

        Args:
            db: Database session
            id: Record ID to delete

        Returns:
            ModelType | None: Deleted record if found, None otherwise
        """
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
