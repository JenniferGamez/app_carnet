"""seed_departamentos

Revision ID: 66c436d7506c
Revises: 151308233f16
Create Date: 2026-03-03 11:03:20.956175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66c436d7506c'
down_revision: Union[str, Sequence[str], None] = '151308233f16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UNIDADES_ACADEMICAS = [
    # Decanatos y Divisiones
    {"nombre": "Decanato de Estudios Generales", "descripcion": "Gestión de Ciclo Básico y Formación General"},
    {"nombre": "Decanato de Estudios Profesionales", "descripcion": "Gestión de Carreras Largas (Sartenejas)"},
    {"nombre": "Decanato de Estudios Tecnológicos", "descripcion": "Gestión de Carreras Cortas y Sedes"},
    {"nombre": "Decanato de Estudios de Postgrado", "descripcion": "Gestión de Especializaciones y Doctorados"},
    {"nombre": "Decanato de Investigación y Desarrollo", "descripcion": "Fomento a la investigación científica"},
    {"nombre": "Decanato de Extensión", "descripcion": "Vinculación con el entorno y comunidad"},
    {"nombre": "División de Ciencias Físicas y Matemáticas", "descripcion": "Unidad Académica Administrativa"},
    {"nombre": "División de Ciencias Sociales y Humanidades", "descripcion": "Unidad Académica Administrativa"},
    {"nombre": "División de Ciencias Biológicas", "descripcion": "Unidad Académica Administrativa"},
    {"nombre": "Div. Ciencias y Tecnologías Admin. e Ind.", "descripcion": "Sede del Litoral"},
    # Departamentos Académicos
    {"nombre": "Dpto. Física", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Química", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Mecánica", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Matemáticas Puras y Aplicadas", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Computación y Tecnología Info.", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Cómputo Científico y Estadística", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Electrónica y Circuitos", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Termodinámica y Fenómenos Transf.", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Conversión y Transporte Energía", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Procesos y Sistemas", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Ciencias de los Materiales", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Ciencias de la Tierra", "descripcion": "División Físicas y Matemáticas"},
    {"nombre": "Dpto. Ciencia y Tecnología Comportamiento", "descripcion": "División Sociales y Humanidades"},
    {"nombre": "Dpto. Lengua y Literatura", "descripcion": "División Sociales y Humanidades"},
    {"nombre": "Dpto. Ciencias Económicas y Admin.", "descripcion": "División Sociales y Humanidades"},
    {"nombre": "Dpto. Idiomas", "descripcion": "División Sociales y Humanidades"},
    {"nombre": "Dpto. Filosofía", "descripcion": "División Sociales y Humanidades"},
    {"nombre": "Dpto. Ciencias Sociales", "descripcion": "División Sociales y Humanidades"},
    {"nombre": "Dpto. Diseño Arq. y Artes Plásticas", "descripcion": "División Sociales y Humanidades"},
    {"nombre": "Dpto. Planificación Urbana", "descripcion": "División Sociales y Humanidades"},
    {"nombre": "Dpto. Biología Celular", "descripcion": "División Ciencias Biológicas"},
    {"nombre": "Dpto. Estudios Ambientales", "descripcion": "División Ciencias Biológicas"},
    {"nombre": "Dpto. Biología de Organismos", "descripcion": "División Ciencias Biológicas"},
    {"nombre": "Dpto. Tecnol. Procesos Biológicos", "descripcion": "División Ciencias Biológicas"},
    {"nombre": "Dpto. Tecnología de Servicios", "descripcion": "División Admin e Industriales (Litoral)"},
    {"nombre": "Dpto. Tecnología Industrial", "descripcion": "División Admin e Industriales (Litoral)"},
    {"nombre": "Dpto. Formación General y C. Básicas", "descripcion": "División Admin e Industriales (Litoral)"},
    # Departamentos de Coordinación Académica
    {"nombre": "Coord. Ingeniería de Computación", "descripcion": "Carrera de Ing. Computación"},
    {"nombre": "Coord. Ingeniería Eléctrica", "descripcion": "Carrera de Ing. Eléctrica"},
    {"nombre": "Coord. Ingeniería Electrónica", "descripcion": "Carrera de Ing. Electrónica"},
    {"nombre": "Coord. Ingeniería Mecánica", "descripcion": "Carrera de Ing. Mecánica"},
    {"nombre": "Coord. Ingeniería Química", "descripcion": "Carrera de Ing. Química"},
    {"nombre": "Coord. Arquitectura", "descripcion": "Carrera de Arquitectura"},
    {"nombre": "Coord. Urbanismo", "descripcion": "Carrera de Urbanismo"},
    {"nombre": "Coord. Licenciatura en Biología", "descripcion": "Carrera de Biología"},
    {"nombre": "Coord. TSU Administración Hotelera", "descripcion": "Carrera TSU Litoral"},
    {"nombre": "Coord. TSU Organización Empresarial", "descripcion": "Carrera TSU Litoral"},
    # Departamentos Administrativos y de Servicio
    {"nombre": "Unidad de Laboratorios", "descripcion": "Gestión de laboratorios de docencia e inv."},
    {"nombre": "Dirección de Servicios Telemáticos", "descripcion": "Infraestructura de red y TI"},
    {"nombre": "Dirección de Admisión y Control Estudios", "descripcion": "Registro académico (DACE)"},
]


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO departamento (nombre, descripcion)
            VALUES (:nombre, :descripcion)
            ON CONFLICT (nombre) DO NOTHING
            """
        ),
        UNIDADES_ACADEMICAS,
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    nombres = [item["nombre"] for item in UNIDADES_ACADEMICAS]
    bind.execute(
        sa.text("DELETE FROM departamento WHERE nombre = ANY(:nombres)"),
        {"nombres": nombres},
    )
