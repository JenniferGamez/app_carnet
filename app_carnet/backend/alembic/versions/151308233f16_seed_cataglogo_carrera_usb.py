"""seed_cataglogo_carrera_usb

Revision ID: 151308233f16
Revises: 8ef064a1a738
Create Date: 2026-03-03 10:23:40.393444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '151308233f16'
down_revision: Union[str, Sequence[str], None] = '6b2c4d9e1f00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CARRERAS = [
    {"codigo": "0100", "nombre": "Ingeniería Eléctrica", "descripcion": "(Sede Sartenejas) Proyectos, ejecución y mantenimiento de sistemas de generación, transmisión y distribución de energía eléctrica."},
    {"codigo": "0200", "nombre": "Ingeniería Mecánica", "descripcion": "(Sede Sartenejas) Diseño, manufactura, instalación y mantenimiento de máquinas, equipos e instalaciones mecánicas."},
    {"codigo": "0300", "nombre": "Ingeniería Química", "descripcion": "(Sede Sartenejas) Aplicación, desarrollo y operación de procesos industriales de transformación de materia y energía."},
    {"codigo": "0400", "nombre": "Licenciatura en Química", "descripcion": "(Sede Sartenejas) Estudio de las áreas fundamentales de la química: inorgánica, orgánica, fisicoquímica y analítica."},
    {"codigo": "0500", "nombre": "Licenciatura en Matemáticas", "descripcion": "(Sede Sartenejas) Formación en disciplinas matemáticas con opciones en estadística, computación y didáctica."},
    {"codigo": "0600", "nombre": "Ingeniería Electrónica", "descripcion": "(Sede Sartenejas) Estudio de sistemas de telecomunicaciones, redes de datos, automatización, control y electrónica industrial."},
    {"codigo": "0700", "nombre": "Arquitectura", "descripcion": "(Sede Sartenejas) Arte y ciencia de proyectar espacios habitables para el desarrollo de las actividades humanas."},
    {"codigo": "0800", "nombre": "Ingeniería de Computación", "descripcion": "(Sede Sartenejas) Estudio de la naturaleza de la información, su almacenamiento, recuperación y sistemas digitales."},
    {"codigo": "1000", "nombre": "Licenciatura en Física", "descripcion": "(Sede Sartenejas) Estudio de las leyes fundamentales de la naturaleza y sus aplicaciones tecnológicas."},
    {"codigo": "1100", "nombre": "Urbanismo", "descripcion": "(Sede Sartenejas) Estudio e intervención de la estructura y dinámica urbana para la mejora de la calidad de vida."},
    {"codigo": "1200", "nombre": "Ingeniería Geofísica", "descripcion": "(Sede Sartenejas) Aplicación de física y matemáticas al estudio de la constitución interna e historia de la Tierra."},
    {"codigo": "1500", "nombre": "Ingeniería de Materiales", "descripcion": "(Sede Sartenejas) Estudio, transformación y aplicación industrial de los materiales según sus propiedades físicas y químicas."},
    {"codigo": "1700", "nombre": "Ingeniería de Producción", "descripcion": "(Sede Sartenejas) Gestión de sistemas productivos, optimización de recursos y procesos industriales."},
    {"codigo": "1800", "nombre": "Ingeniería de Telecomunicaciones", "descripcion": "(Sede Sartenejas) Planificación, diseño y gestión de sistemas de telecomunicaciones de forma eficaz y eficiente."},
    {"codigo": "1900", "nombre": "Licenciatura en Biología", "descripcion": "(Sede Sartenejas) Estudio de los fenómenos biológicos a nivel molecular, celular, individual y poblacional."},
    {"codigo": "3000", "nombre": "Licenciatura en Gestión de la Hospitalidad", "descripcion": "(Sede Litoral) Desempeño efectivo y excelencia en la gestión de servicios de hospitalidad, turismo y hotelería."},
    {"codigo": "3200", "nombre": "Licenciatura en Comercio Internacional", "descripcion": "(Sede Litoral) Gestión de intercambios comerciales, aduanas, negocios globales y políticas de exportación."},
    {"codigo": "4000", "nombre": "Ingeniería de Mantenimiento", "descripcion": "(Sede Litoral) Gerencia, planificación y supervisión del mantenimiento preventivo y correctivo de instalaciones industriales."},
    {"codigo": "1600", "nombre": "Licenciatura en Economía", "descripcion": "(Sede Sartenejas) Análisis de la producción, distribución y consumo de bienes y servicios en la sociedad."},
    {"codigo": "2400", "nombre": "Licenciatura en Estudios y Artes Liberales", "descripcion": "(Sede Sartenejas) Formación en disciplinas de las ciencias sociales y humanidades."},
    {"codigo": "TSU", "nombre": "Tecnología Eléctrica", "descripcion": "(Sedes Litoral y Sartenejas) Participación en proyectos, operación y mantenimiento de sistemas de generación y distribución eléctrica."},
    {"codigo": "TSU", "nombre": "Tecnología Electrónica", "descripcion": "(Sedes Litoral y Sartenejas) Mantenimiento y operación de equipos electrónicos industriales y sistemas de comunicaciones."},
    {"codigo": "TSU", "nombre": "Tecnología Mecánica", "descripcion": "(Sede Litoral) Diseño, construcción, operación y mantenimiento de equipos e instalaciones mecánicas industriales."},
    {"codigo": "TSU", "nombre": "Mantenimiento Aeronáutico", "descripcion": "(Sede Litoral) Mantenimiento preventivo y correctivo de aeronaves y sus sistemas motopropulsores."},
    {"codigo": "TSU", "nombre": "Administración del Turismo", "descripcion": "(Sede Litoral) Gestión y administración operativa de servicios en el sector turístico y recreacional."},
    {"codigo": "TSU", "nombre": "Administración Hotelera", "descripcion": "(Sede Litoral) Desempeño operativo y administrativo en el sector de alojamiento y servicios de hospitalidad."},
    {"codigo": "TSU", "nombre": "Administración del Transporte", "descripcion": "(Sede Litoral) Gestión administrativa y operativa en terminales y empresas de transporte aéreo, marítimo y terrestre."},
    {"codigo": "TSU", "nombre": "Organización Empresarial", "descripcion": "(Sedes Litoral y Sartenejas) Gestión administrativa, contable y operativa en organizaciones productivas y de servicios."},
    {"codigo": "TSU", "nombre": "Comercio Exterior", "descripcion": "(Sedes Litoral y Sartenejas) Integración económica, comercialización internacional y organización de empresas de exportación."},
    {"codigo": "TSU", "nombre": "Administración Aduanera", "descripcion": "(Sede Litoral) Gestión de procesos aduaneros, legislación aduanal y operatividad del comercio exterior."},
]


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    bind.execute(
        sa.text("""
            INSERT INTO carrera (codigo, nombre, descripcion)
            VALUES (:codigo, :nombre, :descripcion)
            ON CONFLICT (nombre) DO NOTHING
        """),
        CARRERAS,
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    nombres = [item["nombre"] for item in CARRERAS]
    bind.execute(
        sa.text("DELETE FROM carrera WHERE nombre = ANY(:nombres)"),
        {"nombres": nombres},
    )
