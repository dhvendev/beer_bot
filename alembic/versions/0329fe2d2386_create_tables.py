"""create tables

Revision ID: 0329fe2d2386
Revises: 13d14acee399
Create Date: 2025-04-30 11:58:29.215424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0329fe2d2386'
down_revision: Union[str, None] = '13d14acee399'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
