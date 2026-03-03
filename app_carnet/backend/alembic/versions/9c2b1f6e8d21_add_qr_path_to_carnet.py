"""add qr_path to carnet

Revision ID: 9c2b1f6e8d21
Revises: 34fe24e89a24
Create Date: 2026-02-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c2b1f6e8d21"
down_revision: Union[str, Sequence[str], None] = "34fe24e89a24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("carnet", sa.Column("qr_path", sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("carnet", "qr_path")
