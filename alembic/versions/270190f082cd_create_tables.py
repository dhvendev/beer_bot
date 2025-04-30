"""create tables

Revision ID: 270190f082cd
Revises: 18718b52c2a0
Create Date: 2025-04-30 11:54:57.582254

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '270190f082cd'
down_revision: Union[str, None] = '18718b52c2a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
