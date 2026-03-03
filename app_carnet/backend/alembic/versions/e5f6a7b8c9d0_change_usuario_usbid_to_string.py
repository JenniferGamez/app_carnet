"""change usuario usbid to string

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-03 13:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "usuario",
        "usbid",
        existing_type=sa.Integer(),
        type_=sa.String(length=45),
        postgresql_using="usbid::text",
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "usuario",
        "usbid",
        existing_type=sa.String(length=45),
        type_=sa.Integer(),
        postgresql_using="usbid::integer",
        existing_nullable=False,
    )
