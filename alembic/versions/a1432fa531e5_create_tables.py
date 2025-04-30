"""create tables

Revision ID: a1432fa531e5
Revises: 4807a1c8ccfc
Create Date: 2025-04-30 12:03:18.821012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1432fa531e5'
down_revision: Union[str, None] = '4807a1c8ccfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
