"""create tables

Revision ID: 13d14acee399
Revises: 09784b8c3a6a
Create Date: 2025-04-30 11:57:06.131007

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13d14acee399'
down_revision: Union[str, None] = '09784b8c3a6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
