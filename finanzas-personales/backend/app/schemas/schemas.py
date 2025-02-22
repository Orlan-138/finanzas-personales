from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import date

# Schemas de Usuario
class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        orm_mode = True

# Schemas de Transacción
class TransaccionBase(BaseModel):
    tipo: str
    monto: float
    fecha: date
    descripcion: str
    categoria: str
    tasa_retorno: Optional[float] = None
    fecha_vencimiento: Optional[date] = None
    tasa_interes: Optional[float] = None
    plazo_meses: Optional[int] = None
    cuota_mensual: Optional[float] = None

class TransaccionCreate(TransaccionBase):
    pass  # No incluimos estado aquí

class Transaccion(TransaccionBase):
    id: int
    usuario_id: int
    estado: Optional[str] = None

    class Config:
        orm_mode = True

class RetornoCreate(BaseModel):
    monto: float
    fecha: date
    descripcion: str
    categoria: str = "retorno_inversion"  # Valor por defecto

# Schemas de Balance
class BalanceDetallado(BaseModel):
    ingresos: float
    gastos: float
    inversiones_activas: float
    retornos_inversiones: float
    creditos_pendientes: float
    pagos_creditos: float
    balance_neto: float
    patrimonio_neto: float

# Schemas de Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

