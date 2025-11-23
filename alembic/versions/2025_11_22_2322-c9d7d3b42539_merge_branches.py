"""merge branches

Revision ID: c9d7d3b42539
Revises: be81b259ef2e, e19835d69ac8
Create Date: 2025-11-22 23:22:55.131111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9d7d3b42539'
down_revision: Union[str, Sequence[str], None] = ('be81b259ef2e', 'e19835d69ac8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
