"""create tables

Revision ID: 4807a1c8ccfc
Revises: 0329fe2d2386
Create Date: 2025-04-30 12:01:02.984283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4807a1c8ccfc'
down_revision: Union[str, None] = '0329fe2d2386'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
