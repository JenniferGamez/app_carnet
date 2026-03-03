"""change carrera pk to nombre

Revision ID: 6b2c4d9e1f00
Revises: 8ef064a1a738
Create Date: 2026-03-03 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6b2c4d9e1f00"
down_revision: Union[str, Sequence[str], None] = "8ef064a1a738"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("estudiante_info_carrera_codigo_fkey", "estudiante_info", type_="foreignkey")
    op.drop_constraint("carrera_pkey", "carrera", type_="primary")

    op.alter_column(
        "carrera",
        "codigo",
        existing_type=sa.Integer(),
        type_=sa.String(length=10),
        postgresql_using="LPAD(codigo::text, 4, '0')",
        nullable=False,
    )
    op.alter_column(
        "carrera",
        "nombre",
        existing_type=sa.String(length=60),
        nullable=False,
    )
    op.create_primary_key("pk_carrera_nombre", "carrera", ["nombre"])

    op.alter_column(
        "estudiante_info",
        "carrera_codigo",
        existing_type=sa.Integer(),
        type_=sa.String(length=10),
        postgresql_using="LPAD(carrera_codigo::text, 4, '0')",
        nullable=True,
    )

    op.add_column("estudiante_info", sa.Column("carrera_nombre", sa.String(length=60), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE estudiante_info ei
            SET carrera_nombre = c.nombre
            FROM carrera c
            WHERE ei.carrera_codigo = c.codigo
            """
        )
    )

    op.alter_column(
        "estudiante_info",
        "carrera_nombre",
        existing_type=sa.String(length=60),
        nullable=False,
    )

    op.create_foreign_key(
        "fk_estudiante_info_carrera_nombre",
        "estudiante_info",
        "carrera",
        ["carrera_nombre"],
        ["nombre"],
    )

    op.drop_column("estudiante_info", "carrera_codigo")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("estudiante_info", sa.Column("carrera_codigo", sa.Integer(), nullable=True))

    op.execute(
        sa.text(
            """
            DELETE FROM estudiante_info
            WHERE carrera_nombre IN (
                SELECT nombre FROM carrera WHERE codigo !~ '^[0-9]+$'
            )
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE estudiante_info ei
            SET carrera_codigo = c.codigo::integer
            FROM carrera c
            WHERE ei.carrera_nombre = c.nombre
              AND c.codigo ~ '^[0-9]+$'
            """
        )
    )

    op.drop_constraint("fk_estudiante_info_carrera_nombre", "estudiante_info", type_="foreignkey")
    op.drop_column("estudiante_info", "carrera_nombre")

    op.alter_column(
        "estudiante_info",
        "carrera_codigo",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.execute(sa.text("DELETE FROM carrera WHERE codigo !~ '^[0-9]+$'"))

    op.drop_constraint("pk_carrera_nombre", "carrera", type_="primary")

    op.alter_column(
        "carrera",
        "codigo",
        existing_type=sa.String(length=10),
        type_=sa.Integer(),
        postgresql_using="codigo::integer",
        nullable=False,
    )
    op.alter_column(
        "carrera",
        "nombre",
        existing_type=sa.String(length=60),
        nullable=True,
    )
    op.create_primary_key("carrera_pkey", "carrera", ["codigo"])

    op.create_foreign_key(
        "estudiante_info_carrera_codigo_fkey",
        "estudiante_info",
        "carrera",
        ["carrera_codigo"],
        ["codigo"],
    )
