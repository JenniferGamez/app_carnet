"""seed bootstrap superadmin

Revision ID: c3d4e5f6a7b8
Revises: b8c9d0e1f2a3
Create Date: 2026-03-03 12:30:00.000000

"""
from typing import Sequence, Union

import os

from alembic import op
import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _resolve_superadmin_password_hash() -> str:
    password_hash = os.getenv("SUPERADMIN_PASSWORD_HASH", "").strip()
    if password_hash:
        return password_hash

    password_plain = os.getenv("SUPERADMIN_PASSWORD", "").strip()
    if password_plain:
        return pbkdf2_sha256.hash(password_plain)

    raise RuntimeError(
        "Define SUPERADMIN_PASSWORD_HASH o SUPERADMIN_PASSWORD para bootstrap de SuperAdmin"
    )


def _resolve_superadmin_usbid() -> str:
    raw_value = os.getenv("SUPERADMIN_USBID", "superadmin").strip()
    if not raw_value:
        raise RuntimeError("SUPERADMIN_USBID no puede estar vacío")
    return raw_value


def _resolve_departamento_id(bind) -> int:
    raw_departamento = os.getenv("SUPERADMIN_DEPARTAMENTO_ID", "").strip()
    if raw_departamento:
        try:
            candidate_id = int(raw_departamento)
        except ValueError as exc:
            raise RuntimeError("SUPERADMIN_DEPARTAMENTO_ID debe ser numérico") from exc

        exists = bind.execute(
            sa.text("SELECT 1 FROM departamento WHERE id = :id LIMIT 1"),
            {"id": candidate_id},
        ).scalar()
        if exists:
            return candidate_id

    departamento_id = bind.execute(sa.text("SELECT id FROM departamento ORDER BY id ASC LIMIT 1")).scalar()
    if departamento_id is None:
        raise RuntimeError("No existe ningún departamento para asociar el SuperAdmin")
    return int(departamento_id)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    superadmin_usbid = _resolve_superadmin_usbid()
    superadmin_password_hash = _resolve_superadmin_password_hash()
    superadmin_departamento_id = _resolve_departamento_id(bind)
    superadmin_descripcion = os.getenv("SUPERADMIN_DESCRIPCION", "Usuario bootstrap SuperAdmin").strip()

    bind.execute(
        sa.text(
            """
            INSERT INTO rol (nombre, descripcion)
            VALUES ('SuperAdmin', 'Acceso total al sistema')
            ON CONFLICT (nombre) DO NOTHING
            """
        )
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO usuario (
                usbid,
                password,
                descripcion,
                activo,
                rol_nombre,
                persona_carnet_usbid,
                departamento_id
            )
            VALUES (
                :usbid,
                :password,
                :descripcion,
                TRUE,
                'SuperAdmin',
                NULL,
                :departamento_id
            )
            ON CONFLICT (usbid) DO UPDATE SET
                password = EXCLUDED.password,
                descripcion = EXCLUDED.descripcion,
                activo = TRUE,
                rol_nombre = 'SuperAdmin',
                departamento_id = EXCLUDED.departamento_id
            """
        ),
        {
            "usbid": superadmin_usbid,
            "password": superadmin_password_hash,
            "descripcion": superadmin_descripcion,
            "departamento_id": superadmin_departamento_id,
        },
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    superadmin_usbid = _resolve_superadmin_usbid()

    bind.execute(
        sa.text(
            """
            DELETE FROM usuario
            WHERE usbid = :usbid
              AND rol_nombre = 'SuperAdmin'
            """
        ),
        {"usbid": superadmin_usbid},
    )
