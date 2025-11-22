"""CRUD operations module."""

from app.crud.base import CRUDBase
from app.crud.user import user

__all__ = ["CRUDBase", "user"]
