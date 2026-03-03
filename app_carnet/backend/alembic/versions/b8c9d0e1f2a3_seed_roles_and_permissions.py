"""seed roles and permissions

Revision ID: b8c9d0e1f2a3
Revises: a7b1c2d3e4f5
Create Date: 2026-03-03 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "a7b1c2d3e4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLES = [
    {"nombre": "SuperAdmin", "descripcion": "Acceso total al sistema"},
    {"nombre": "Admin", "descripcion": "Operación de registro y emisión"},
    {"nombre": "Consulta", "descripcion": "Acceso de solo lectura"},
]

PERMISOS = [
    # Permisos de gestión de usuarios
    {"nombre": "usuario.crear", "descripcion": "Crear usuarios"},
    {"nombre": "usuario.leer", "descripcion": "Ver usuarios"},
    {"nombre": "usuario.editar", "descripcion": "Editar usuarios"},
    {"nombre": "usuario.eliminar", "descripcion": "Eliminar usuarios"},
    # Permisos de gestión de personas
    {"nombre": "persona.crear", "descripcion": "Crear personas"},
    {"nombre": "persona.leer", "descripcion": "Ver personas"},
    {"nombre": "persona.editar", "descripcion": "Editar personas"},
    # Permisos de gestión de carnets
    {"nombre": "carnet.crear", "descripcion": "Emitir carnets"},
    {"nombre": "carnet.leer", "descripcion": "Ver carnets"},
    {"nombre": "carnet.editar", "descripcion": "Actualizar carnets"},
    {"nombre": "carnet.anular", "descripcion": "Anular o suspender carnets"},
    # Permisos de gestión de códigos QR
    {"nombre": "qr.generar", "descripcion": "Generar códigos QR para carnets"},
    {"nombre": "qr.leer", "descripcion": "Ver información de códigos QR"},
    # Permisos de gestión de afiliaciones
    {"nombre": "afiliacion.crear", "descripcion": "Crear afiliaciones"},
    {"nombre": "afiliacion.leer", "descripcion": "Ver afiliaciones"},
    {"nombre": "afiliacion.editar", "descripcion": "Editar afiliaciones"},
    {"nombre": "afiliacion.gestionar", "descripcion": "Gestionar afiliaciones"},
    # Permisos de asignación
    {"nombre": "departamento.asignar", "descripcion": "Asignar o cambiar departamento"},
    {"nombre": "carrera.asignar", "descripcion": "Asignar o cambiar carrera"},
    # Permisos de cargar archivos (CSV, TXT, etc.)
    {"nombre": "archivo.cargar", "descripcion": "Cargar archivos al sistema"},
    # Permisos de gestión de fotos
    {"nombre": "foto.cargar", "descripcion": "Cargar fotos de personas"},
    {"nombre": "foto.leer", "descripcion": "Ver fotos de personas"},
    {"nombre": "foto.editar", "descripcion": "Editar fotos de personas"},
    
]

ROLE_PERMISSIONS = {
    "SuperAdmin": [
        "*",
    ],
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
            unknown = [p for p in permission_list if p not in known_permissions]
            if unknown:
                raise ValueError(
                    f"Permisos no definidos para rol '{role_name}': {', '.join(unknown)}"
                )
            resolved = permission_list

        rows.extend(
            {"rol_nombre": role_name, "permisos_nombre": permission_name}
            for permission_name in resolved
        )

    return rows


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    bind.execute(
        sa.text(
            """
            INSERT INTO rol (nombre, descripcion)
            VALUES (:nombre, :descripcion)
            ON CONFLICT (nombre) DO NOTHING
            """
        ),
        ROLES,
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO permisos (nombre, descripcion)
            VALUES (:nombre, :descripcion)
            ON CONFLICT (nombre) DO NOTHING
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


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()

    role_names = [item["nombre"] for item in ROLES]
    permission_names = [item["nombre"] for item in PERMISOS]

    bind.execute(
        sa.text(
            """
            DELETE FROM rol_has_permisos
            WHERE rol_nombre = ANY(:role_names)
               OR permisos_nombre = ANY(:permission_names)
            """
        ),
        {"role_names": role_names, "permission_names": permission_names},
    )

    bind.execute(
        sa.text("DELETE FROM rol WHERE nombre = ANY(:role_names)"),
        {"role_names": role_names},
    )

    bind.execute(
        sa.text("DELETE FROM permisos WHERE nombre = ANY(:permission_names)"),
        {"permission_names": permission_names},
    )
