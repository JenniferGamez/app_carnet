from sqlalchemy.orm import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    Float,
    Boolean,
    ForeignKey,
    ForeignKeyConstraint,
    Table,
    UniqueConstraint,
    Enum as SQLEnum,
)

class TipoAccesoEnum(PyEnum):
    Entrada = "Entrada"
    Salida = "Salida"


class ResultadoEnum(PyEnum):
    Permitido = "Permitido"
    Denegado = "Denegado"


class SexoEnum(PyEnum):
    M = "M"
    F = "F"


class TipoPuntoAccesoEnum(PyEnum):
    Torniquete = "Torniquete"
    Garita = "Garita"
    Puerta = "Puerta"


class TipoVehiculoEnum(PyEnum):
    Automovil = "Automóvil"
    Motocicleta = "Motocicleta"
    Autobus = "Autobús"
    Van = "Van"
    Bicicleta = "Bicicleta"
    
    
class NacionalidadEnum(PyEnum):
    V = "Venezolano"
    E = "Extranjero"