from sqlalchemy import Column, ForeignKeyConstraint, String, Integer, ForeignKey, Date, Boolean, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship, foreign
from app.models.base import Base
from sqlalchemy import DateTime, func

class Usuario(Base):
    __tablename__ = "usuario"

    usbid = Column(String(45), primary_key=True)
    password = Column(String(255), nullable=False)
    descripcion = Column(String(60))
    created_at = Column(DateTime, server_default=func.now())
    activo = Column(Boolean, default=True)
    rol_nombre = Column(String(45), ForeignKey("rol.nombre"), nullable=False)
    remote_ip = Column(String(45))
    remote_access_from = Column(String(45))
    persona_carnet_usbid = Column(String(45), ForeignKey("carnet.usbid"))
    departamento_id = Column(Integer, ForeignKey("departamento.id"), nullable=False)

    persona = relationship(
        "Persona",
        primaryjoin="foreign(Usuario.persona_carnet_usbid)==Persona.carnet_usbid",
        viewonly=True,
    )
    rol = relationship("Rol")
    departamento = relationship("Departamento")

class Permisos(Base):
    __tablename__ = "permisos"

    nombre = Column(String(45), primary_key=True)
    descripcion = Column(String(100))


rol_has_permisos = Table(
    "rol_has_permisos",
    Base.metadata,
    Column("rol_nombre", String(45), ForeignKey("rol.nombre"), primary_key=True),
    Column("permisos_nombre", String(45), ForeignKey("permisos.nombre"), primary_key=True),
)

class Rol(Base):
    __tablename__ = "rol"

    nombre = Column(String(45), primary_key=True)
    descripcion = Column(String(100))
    permisos = relationship(
        "Permisos",
        secondary=rol_has_permisos,
        backref="roles"
    )

class Departamento(Base):
    __tablename__ = "departamento"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(45), nullable=False, unique=True)
    descripcion = Column(String(45))