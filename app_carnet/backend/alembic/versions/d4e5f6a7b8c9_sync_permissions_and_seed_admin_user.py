"""sync permissions and seed admin user

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-03 13:10:00.000000

"""
from typing import Sequence, Union

import os

from alembic import op
import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLES = [
    {"nombre": "SuperAdmin", "descripcion": "Acceso total al sistema"},
    {"nombre": "Admin", "descripcion": "Operación de registro y emisión"},
    {"nombre": "Consulta", "descripcion": "Acceso de solo lectura"},
]

PERMISOS = [
    {"nombre": "usuario.crear", "descripcion": "Crear usuarios"},
    {"nombre": "usuario.leer", "descripcion": "Ver usuarios"},
    {"nombre": "usuario.editar", "descripcion": "Editar usuarios"},
    {"nombre": "usuario.eliminar", "descripcion": "Eliminar usuarios"},
    {"nombre": "persona.crear", "descripcion": "Crear personas"},
    {"nombre": "persona.leer", "descripcion": "Ver personas"},
    {"nombre": "persona.editar", "descripcion": "Editar personas"},
    {"nombre": "carnet.crear", "descripcion": "Emitir carnets"},
    {"nombre": "carnet.leer", "descripcion": "Ver carnets"},
    {"nombre": "carnet.editar", "descripcion": "Actualizar carnets"},
    {"nombre": "carnet.anular", "descripcion": "Anular o suspender carnets"},
    {"nombre": "qr.generar", "descripcion": "Generar códigos QR para carnets"},
    {"nombre": "qr.leer", "descripcion": "Ver información de códigos QR"},
    {"nombre": "afiliacion.crear", "descripcion": "Crear afiliaciones"},
    {"nombre": "afiliacion.leer", "descripcion": "Ver afiliaciones"},
    {"nombre": "afiliacion.editar", "descripcion": "Editar afiliaciones"},
    {"nombre": "afiliacion.gestionar", "descripcion": "Gestionar afiliaciones"},
    {"nombre": "departamento.asignar", "descripcion": "Asignar o cambiar departamento"},
    {"nombre": "carrera.asignar", "descripcion": "Asignar o cambiar carrera"},
    {"nombre": "archivo.cargar", "descripcion": "Cargar archivos al sistema"},
    {"nombre": "foto.cargar", "descripcion": "Cargar fotos de personas"},
    {"nombre": "foto.leer", "descripcion": "Ver fotos de personas"},
    {"nombre": "foto.editar", "descripcion": "Editar fotos de personas"},
]

ROLE_PERMISSIONS = {
    "SuperAdmin": ["*"],
    "Admin": [
        "persona.leer",
        "persona.crear",
        "persona.editar",
        "carnet.leer",
        "carnet.crear",
        "carnet.editar",
        "carnet.anular",
        "qr.generar",
        "qr.leer",
        "afiliacion.crear",
        "afiliacion.leer",
        "afiliacion.editar",
        "afiliacion.gestionar",
        "departamento.asignar",
        "carrera.asignar",
        "archivo.cargar",
        "foto.cargar",
        "foto.leer",
        "foto.editar",
    ],
    "Consulta": [
        "persona.leer",
        "carnet.leer",
        "usuario.leer",
        "qr.leer",
        "afiliacion.leer",
        "foto.leer",
    ],
}


def _resolve_role_permissions() -> list[dict[str, str]]:
    known_permissions = {item["nombre"] for item in PERMISOS}
    rows: list[dict[str, str]] = []

    for role_name, permission_list in ROLE_PERMISSIONS.items():
        if "*" in permission_list:
            resolved = sorted(known_permissions)
        else:
            unknown = [permission for permission in permission_list if permission not in known_permissions]
            if unknown:
                raise RuntimeError(
                    f"Permisos no definidos para rol '{role_name}': {', '.join(unknown)}"
                )
            resolved = permission_list

        rows.extend(
            {"rol_nombre": role_name, "permisos_nombre": permission_name}
            for permission_name in resolved
        )

    return rows


def _resolve_admin_usbid() -> str:
    raw_value = os.getenv("ADMIN_USBID", "admin").strip()
    if not raw_value:
        raise RuntimeError("ADMIN_USBID no puede estar vacío")
    return raw_value


def _resolve_admin_password_hash() -> str:
    password_hash = os.getenv("ADMIN_PASSWORD_HASH", "").strip()
    if password_hash:
        return password_hash

    password_plain = os.getenv("ADMIN_PASSWORD", "usb2026admin").strip()
    if not password_plain:
        raise RuntimeError("Define ADMIN_PASSWORD o ADMIN_PASSWORD_HASH")

    return pbkdf2_sha256.hash(password_plain)


def _resolve_departamento_id(bind) -> int:
    raw_departamento = os.getenv("ADMIN_DEPARTAMENTO_ID", "").strip()
    if raw_departamento:
        try:
            candidate_id = int(raw_departamento)
        except ValueError as exc:
            raise RuntimeError("ADMIN_DEPARTAMENTO_ID debe ser numérico") from exc

        exists = bind.execute(
            sa.text("SELECT 1 FROM departamento WHERE id = :id LIMIT 1"),
            {"id": candidate_id},
        ).scalar()
        if exists:
            return candidate_id

    departamento_id = bind.execute(sa.text("SELECT id FROM departamento ORDER BY id ASC LIMIT 1")).scalar()
    if departamento_id is None:
        raise RuntimeError("No existe ningún departamento para asociar el usuario Admin")

    return int(departamento_id)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    bind.execute(
        sa.text(
            """
            INSERT INTO rol (nombre, descripcion)
            VALUES (:nombre, :descripcion)
            ON CONFLICT (nombre) DO UPDATE SET
                descripcion = EXCLUDED.descripcion
            """
        ),
        ROLES,
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO permisos (nombre, descripcion)
            VALUES (:nombre, :descripcion)
            ON CONFLICT (nombre) DO UPDATE SET
                descripcion = EXCLUDED.descripcion
            """
        ),
        PERMISOS,
    )

    role_permission_rows = _resolve_role_permissions()

    bind.execute(
        sa.text(
            """
            INSERT INTO rol_has_permisos (rol_nombre, permisos_nombre)
            VALUES (:rol_nombre, :permisos_nombre)
            ON CONFLICT (rol_nombre, permisos_nombre) DO NOTHING
            """
        ),
        role_permission_rows,
    )

    admin_usbid = _resolve_admin_usbid()
    admin_password_hash = _resolve_admin_password_hash()
    admin_departamento_id = _resolve_departamento_id(bind)
    admin_descripcion = os.getenv("ADMIN_DESCRIPCION", "Usuario Admin de pruebas").strip()

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
                'Admin',
                NULL,
                :departamento_id
            )
            ON CONFLICT (usbid) DO UPDATE SET
                password = EXCLUDED.password,
                descripcion = EXCLUDED.descripcion,
                activo = TRUE,
                rol_nombre = 'Admin',
                departamento_id = EXCLUDED.departamento_id
            """
        ),
        {
            "usbid": admin_usbid,
            "password": admin_password_hash,
            "descripcion": admin_descripcion,
            "departamento_id": admin_departamento_id,
        },
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()

    admin_usbid = _resolve_admin_usbid()
    role_names = [item["nombre"] for item in ROLES]
    permission_names = [item["nombre"] for item in PERMISOS]

    bind.execute(
        sa.text(
            """
            DELETE FROM usuario
            WHERE usbid = :usbid
              AND rol_nombre = 'Admin'
            """
        ),
        {"usbid": admin_usbid},
    )

    bind.execute(
        sa.text(
            """
            DELETE FROM rol_has_permisos
            WHERE rol_nombre = ANY(:role_names)
              AND permisos_nombre = ANY(:permission_names)
            """
        ),
        {"role_names": role_names, "permission_names": permission_names},
    )
