from sqlalchemy import Column, ForeignKeyConstraint, Numeric, String, Integer, ForeignKey, Date, Boolean, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from app.models.base import Base


class Afiliacion(Base):
    __tablename__ = "afiliacion"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(45), nullable=False)
    descripcion = Column(String(150))
    prioridad = Column(Integer)
    duracion_vigencia_anos = Column(Integer)
    requiere_pago_estacionamiento = Column(Boolean)

class StatusPersonaAfiliacion(Base):
    __tablename__ = "status_persona_afiliacion"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(45), nullable=False, unique=True)


class Sede(Base):
    __tablename__ = "sede"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(45), nullable=False, unique=True)
    direccion = Column(String(150), nullable=False)


class PersonaTieneAfiliacion(Base):
    __tablename__ = "persona_tiene_afiliacion"

    persona_cedula = Column(String(30), ForeignKey("persona.cedula"), primary_key=True)
    afiliacion_id = Column(Integer, ForeignKey("afiliacion.id"), primary_key=True)
    status_persona_id = Column(Integer, ForeignKey("status_persona_afiliacion.id"), nullable=False)
    sede_id = Column(Integer, ForeignKey("sede.id"), nullable=False)
    observaciones_desincorporacion = Column(String(300))
    fecha_desincorporacion = Column(Date)
    fecha_incorporacion = Column(Date)

    status = relationship("StatusPersonaAfiliacion")
    sede = relationship("Sede")
    persona = relationship("Persona")
    afiliacion = relationship("Afiliacion")

class Carrera(Base):
    __tablename__ = "carrera"

    codigo = Column(String(10), nullable=False)
    nombre = Column(String(60), primary_key=True, nullable=False)
    descripcion = Column(String(150))


class EstudianteInfo(Base):
    __tablename__ = "estudiante_info"

    persona_tiene_afiliacion_persona_cedula = Column(String(30), primary_key=True)
    persona_tiene_afiliacion_afiliacion_id = Column(Integer, primary_key=True)
    es_deportista = Column(Boolean)
    autorizado_desayuno = Column(Boolean)
    autorizado_almuerzo = Column(Boolean)
    autorizado_cena = Column(Boolean)
    tad = Column(String(45))
    trd = Column(String(45))
    taa = Column(String(45))
    tra = Column(String(45))
    tac = Column(String(45))
    trc = Column(String(45))
    carrera_nombre = Column(String(60), ForeignKey("carrera.nombre"), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["persona_tiene_afiliacion_persona_cedula", "persona_tiene_afiliacion_afiliacion_id"],
            ["persona_tiene_afiliacion.persona_cedula", "persona_tiene_afiliacion.afiliacion_id"],
    ),
)

    carrera = relationship("Carrera")


class TrabajadorInfo(Base):
    __tablename__ = "trabajador_info"

    persona_tiene_afiliacion_persona_cedula = Column(String(30), primary_key=True)
    persona_tiene_afiliacion_afiliacion_id = Column(Integer, primary_key=True)
    codtpe = Column(Integer, nullable=False)
    sueldo = Column(Numeric(10,5))
    bono = Column(Numeric(10,5))
    tad = Column(String(45))
    trd = Column(String(45))
    taa = Column(String(45))
    tra = Column(String(45))
    tac = Column(String(45))
    trc = Column(String(45))
    autorizado_desayuno = Column(Boolean)
    autorizado_almuerzo = Column(Boolean)
    autorizado_cena = Column(Boolean)

    __table_args__ = (
        ForeignKeyConstraint(
            ["persona_tiene_afiliacion_persona_cedula", "persona_tiene_afiliacion_afiliacion_id"],
            ["persona_tiene_afiliacion.persona_cedula", "persona_tiene_afiliacion.afiliacion_id"],
    ),
)