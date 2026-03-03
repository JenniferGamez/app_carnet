"""seed catalogos iniciales

Revision ID: 8ef064a1a738
Revises: 9c2b1f6e8d21
Create Date: 2026-03-03 10:13:03.051920

"""
from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ef064a1a738'
down_revision: Union[str, Sequence[str], None] = '9c2b1f6e8d21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def _insert_if_not_exists(bind, table_name: str, nombre: str, direccion: Optional[str] = None) -> None:
    if direccion is None:
        bind.execute(
            sa.text(
                f"""
                INSERT INTO {table_name} (nombre)
                SELECT :nombre
                WHERE NOT EXISTS (
                    SELECT 1 FROM {table_name} WHERE nombre = :nombre
                )
                """
            ),
            {"nombre": nombre},
        )
        return

    bind.execute(
        sa.text(
            f"""
            INSERT INTO {table_name} (nombre, direccion)
            SELECT :nombre, :direccion
            WHERE NOT EXISTS (
                SELECT 1 FROM {table_name} WHERE nombre = :nombre
            )
            """
        ),
        {"nombre": nombre, "direccion": direccion},
    )


def upgrade() -> None:
    bind = op.get_bind()

    _insert_if_not_exists(bind, "status_carnet", "Vigente")
    _insert_if_not_exists(bind, "status_carnet", "Vencido")
    _insert_if_not_exists(bind, "status_carnet", "Suspendido")

    _insert_if_not_exists(
        bind,
        "sede",
        "Litoral",
        "Valle de Camurí Grande, Parroquia Naiguatá, Municipio Vargas, Estado La Guaira, Venezuela.",
    )
    _insert_if_not_exists(
        bind,
        "sede",
        "Sartenejas",
        "Carretera de Hoyo de la Puerta, Valle de Sartenejas, Municipio Baruta, Estado Miranda, Venezuela.",
    )


def downgrade() -> None:
    bind = op.get_bind()

    bind.execute(
        sa.text(
            """
            DELETE FROM sede
            WHERE nombre IN ('Litoral', 'Sartenejas')
            """
        )
    )

    bind.execute(
        sa.text(
            """
            DELETE FROM status_carnet
            WHERE nombre IN ('Vigente', 'Vencido', 'Suspendido')
            """
        )
    )