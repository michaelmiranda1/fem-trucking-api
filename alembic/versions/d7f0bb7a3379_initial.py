"""initial

Revision ID: d7f0bb7a3379
Revises: None
Create Date: 2026-02-11 00:11:35.359283
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7f0bb7a3379"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This migration is intentionally empty.
    # Your schema was already created by the previous initial migration.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass