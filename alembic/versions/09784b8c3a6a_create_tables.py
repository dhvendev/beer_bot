"""create tables

Revision ID: 09784b8c3a6a
Revises: 86afbe75c12b
Create Date: 2025-04-30 11:55:26.945195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09784b8c3a6a'
down_revision: Union[str, None] = '86afbe75c12b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
