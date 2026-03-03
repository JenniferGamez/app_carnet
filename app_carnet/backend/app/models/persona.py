from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Date, Boolean, Enum as SQLEnum, Table, func
from sqlalchemy.orm import relationship
from app.models.base import Base, SexoEnum, TipoVehiculoEnum, NacionalidadEnum


class Persona(Base):
    __tablename__ = "persona"

    cedula = Column(String(15), primary_key=True)
    carnet_usbid = Column(String(45), ForeignKey("carnet.usbid"))
    nacionalidad = Column(SQLEnum(NacionalidadEnum), nullable=False)
    nombres = Column(String(60), nullable=False)
    apellidos = Column(String(60), nullable=False)
    email = Column(String(120), unique=True)
    direccion = Column(String(150))
    sexo = Column(SQLEnum(SexoEnum), nullable=False)
    telefono_1 = Column(String(20))
    telefono_2 = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    discapacidad = Column(Boolean, nullable=False)

    carnet = relationship("Carnet")
    vehiculos = relationship("Vehiculo", back_populates="persona", cascade="all, delete")


class Foto(Base):
    __tablename__ = "foto"

    id = Column(Integer, primary_key=True)
    persona_cedula = Column(String(15), ForeignKey("persona.cedula"), nullable=False)
    foto_path = Column(String(400))

    persona = relationship("Persona")

class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id = Column(Integer, primary_key=True)
    persona_cedula = Column(String(15), ForeignKey("persona.cedula"), nullable=False)
    placa = Column(String(10), unique=True, nullable=False)
    tipo_vehiculo = Column(SQLEnum(TipoVehiculoEnum))
    marca = Column(String(45), nullable=False)
    modelo = Column(String(45), nullable=False)
    color = Column(String(45), nullable=False)

    persona = relationship("Persona", back_populates="vehiculos")