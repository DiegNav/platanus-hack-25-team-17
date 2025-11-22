"""CRUD operations for User model."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model with additional methods."""

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """Get user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User | None: User if found, None otherwise
        """
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> User | None:
        """Get user by username.

        Args:
            db: Database session
            username: Username

        Returns:
            User | None: User if found, None otherwise
        """
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create new user with hashed password.

        Args:
            db: Database session
            obj_in: User creation schema

        Returns:
            User: Created user
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate | dict[str, any]
    ) -> User:
        """Update user with password hashing if password is provided.

        Args:
            db: Database session
            db_obj: User database object
            obj_in: User update schema or dict

        Returns:
            User: Updated user
        """
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> User | None:
        """Authenticate a user.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            User | None: User if authenticated, None otherwise
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        """Check if user is active.

        Args:
            user: User object

        Returns:
            bool: True if user is active
        """
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """Check if user is superuser.

        Args:
            user: User object

        Returns:
            bool: True if user is superuser
        """
        return user.is_superuser


user = CRUDUser(User)
