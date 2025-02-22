from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from ..database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    nombre = Column(String)
    password_hash = Column(String)

    # Relación con transacciones
    transacciones = relationship("Transaccion", back_populates="usuario")

class TipoTransaccion(PyEnum):
    INGRESO = "ingreso"
    GASTO = "gasto"
    INVERSION = "inversion"
    CREDITO = "credito"
    RETORNO_INVERSION = "retorno_inversion"
    PAGO_CREDITO = "pago_credito"

class Transaccion(Base):
    __tablename__ = "transacciones"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo = Column(String)
    monto = Column(Float)
    fecha = Column(Date)
    descripcion = Column(String)
    categoria = Column(String)
    
    # Campos específicos para inversiones
    tasa_retorno = Column(Float, nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)
    estado = Column(String, nullable=True)  # "activa", "finalizada", "en_curso"
    inversion_relacionada_id = Column(Integer, ForeignKey("transacciones.id"), nullable=True)
    
    # Campos específicos para créditos
    tasa_interes = Column(Float, nullable=True)
    plazo_meses = Column(Integer, nullable=True)
    cuota_mensual = Column(Float, nullable=True)
    
    # Relación con usuario
    usuario = relationship("Usuario", back_populates="transacciones")