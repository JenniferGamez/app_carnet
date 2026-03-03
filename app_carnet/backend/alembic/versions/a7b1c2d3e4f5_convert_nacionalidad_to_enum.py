"""convert nacionalidad to enum

Revision ID: a7b1c2d3e4f5
Revises: 66c436d7506c
Create Date: 2026-03-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7b1c2d3e4f5"
down_revision: Union[str, Sequence[str], None] = "66c436d7506c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    nacionalidad_enum = sa.Enum("V", "E", name="nacionalidadenum")
    nacionalidad_enum.create(op.get_bind(), checkfirst=True)
    op.add_column("persona", sa.Column("nacionalidad", nacionalidad_enum, nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE persona p
            SET nacionalidad = CASE
                WHEN n.nombre ILIKE 'venez%' THEN 'V'::nacionalidadenum
                WHEN n.nombre ILIKE 'extra%' THEN 'E'::nacionalidadenum
                ELSE 'E'::nacionalidadenum
            END
            FROM nacionalidad n
            WHERE p.nacionalidad_id = n.id
            """
        )
    )

    op.execute(sa.text("UPDATE persona SET nacionalidad = 'V'::nacionalidadenum WHERE nacionalidad IS NULL"))

    op.alter_column(
        "persona",
        "nacionalidad",
        existing_type=sa.Enum("V", "E", name="nacionalidadenum"),
        nullable=False,
    )

    op.drop_constraint("persona_nacionalidad_id_fkey", "persona", type_="foreignkey")
    op.drop_column("persona", "nacionalidad_id")
    op.drop_table("nacionalidad")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "nacionalidad",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=45), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO nacionalidad (id, nombre)
            VALUES (1, 'Venezolano'), (2, 'Extranjero')
            ON CONFLICT (id) DO NOTHING
            """
        )
    )

    op.add_column("persona", sa.Column("nacionalidad_id", sa.Integer(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE persona
            SET nacionalidad_id = CASE
                WHEN nacionalidad = 'V' THEN 1
                WHEN nacionalidad = 'E' THEN 2
                ELSE 1
            END
            """
        )
    )

    op.create_foreign_key(
        "persona_nacionalidad_id_fkey",
        "persona",
        "nacionalidad",
        ["nacionalidad_id"],
        ["id"],
    )

    op.drop_column("persona", "nacionalidad")
    sa.Enum("V", "E", name="nacionalidadenum").drop(op.get_bind(), checkfirst=True)
