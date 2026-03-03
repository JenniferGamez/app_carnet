from sqlalchemy import Column, DateTime, Numeric, String, Integer, ForeignKey, Date, Enum as SQLEnum, Table, Time, func
from sqlalchemy.orm import relationship
from app.models.base import Base, ResultadoEnum, TipoAccesoEnum, TipoPuntoAccesoEnum

# Relación carnet <-> punto de acceso (muchos a muchos)
carnet_punto_acceso = Table(
    "carnet_has_punto_acceso",
    Base.metadata,
    Column("carnet_usbid", String(10), ForeignKey("carnet.usbid"), primary_key=True),
    Column("punto_acceso_id", Integer, ForeignKey("punto_acceso.id"), primary_key=True),
)

class StatusCarnet(Base):
    __tablename__ = "status_carnet"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(45), nullable=False, unique=True)


class Carnet(Base):
    __tablename__ = "carnet"

    usbid = Column(String(10), primary_key=True)
    fecha_emision = Column(Date)
    fecha_vencimiento = Column(Date)
    uuid = Column(String(36), unique=True, nullable=False) 
    status_carnet_id = Column(Integer, ForeignKey("status_carnet.id"), nullable=False)

    status = relationship("StatusCarnet")
    puntos_acceso = relationship("PuntoAcceso", secondary=carnet_punto_acceso, back_populates="carnets")
    

class CuentaSaldo(Base):
    __tablename__ = "cuenta_saldo"

    id = Column(Integer, primary_key=True)
    saldo_actual = Column(Numeric(10,6), default=0)
    updated_at = Column(DateTime, onupdate=func.now())
    carnet_usbid = Column(String(10), ForeignKey("carnet.usbid"), unique=True)

    carnet = relationship("Carnet")

class PuntoAcceso(Base):
    __tablename__ = "punto_acceso"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(45), nullable=False)
    tipo = Column(SQLEnum(TipoPuntoAccesoEnum))
    ubicacion = Column(String(100))

    accesos = relationship("Acceso", back_populates="punto_acceso")
    carnets = relationship("Carnet", secondary=carnet_punto_acceso, back_populates="puntos_acceso")


class Acceso(Base):
    __tablename__ = "acceso"

    id = Column(Integer, primary_key=True)
    tipo_acceso = Column(SQLEnum(TipoAccesoEnum))
    fecha_hora = Column(Time)
    resultado = Column(SQLEnum(ResultadoEnum))
    punto_acceso_id = Column(Integer, ForeignKey("punto_acceso.id"), nullable=False)

    punto_acceso = relationship("PuntoAcceso", back_populates="accesos")