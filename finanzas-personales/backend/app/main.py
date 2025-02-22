from sqlalchemy import func
from datetime import timedelta, date
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy import func
from datetime import timedelta
from typing import List  # Agregamos esta importación
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .database import engine, get_db
from .models import models
from .schemas import schemas
from .security import (
    verify_password, 
    get_password_hash,
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finanzas Personales API")

# Definir oauth2_scheme antes de usarlo
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return False
    print(f"Usuario autenticado: {user.nombre}")  # Verifica que el nombre se recupere
    return user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    print(f"Token generado para: {user.nombre}")  # Verifica que el nombre se devuelva
    return {"access_token": access_token, "token_type": "bearer", "nombre": user.nombre}

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.Usuario).filter(models.Usuario.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/users/me/", response_model=schemas.Usuario)
async def read_users_me(current_user: models.Usuario = Depends(get_current_user)):
    return current_user

# Mantén el endpoint de crear usuario que ya teníamos
@app.post("/usuarios/", response_model=schemas.Usuario)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    db_usuario = models.Usuario(
        email=usuario.email,
        nombre=usuario.nombre,
        password_hash=get_password_hash(usuario.password)
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    print(f"Usuario creado: {db_usuario.nombre}")
    return db_usuario

@app.post("/transacciones/", response_model=schemas.Transaccion)
async def crear_transaccion(
    transaccion: schemas.TransaccionCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_transaccion = models.Transaccion(
        **transaccion.dict(),
        usuario_id=current_user.id
    )
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@app.get("/transacciones/", response_model=List[schemas.Transaccion])
async def listar_transacciones(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == current_user.id
    ).all()

@app.get("/transacciones/{transaccion_id}", response_model=schemas.Transaccion)
async def obtener_transaccion(
    transaccion_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaccion = db.query(models.Transaccion).filter(
        models.Transaccion.id == transaccion_id,
        models.Transaccion.usuario_id == current_user.id
    ).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaccion

@app.put("/transacciones/{transaccion_id}", response_model=schemas.Transaccion)
async def actualizar_transaccion(
    transaccion_id: int,
    transaccion: schemas.TransaccionCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_transaccion = db.query(models.Transaccion).filter(
        models.Transaccion.id == transaccion_id,
        models.Transaccion.usuario_id == current_user.id
    ).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    for key, value in transaccion.dict().items():
        setattr(db_transaccion, key, value)
    
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@app.delete("/transacciones/{transaccion_id}")
async def eliminar_transaccion(
    transaccion_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_transaccion = db.query(models.Transaccion).filter(
        models.Transaccion.id == transaccion_id,
        models.Transaccion.usuario_id == current_user.id
    ).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    db.delete(db_transaccion)
    db.commit()
    return {"message": "Transacción eliminada"}

@app.get("/transacciones/resumen/", response_model=schemas.BalanceDetallado)
async def obtener_resumen(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == current_user.id
    )
    
    # Aplicar filtros de fecha
    if fecha_inicio:
        query = query.filter(models.Transaccion.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(models.Transaccion.fecha <= fecha_fin)
    
    # Calcular totales por tipo
    ingresos = sum(t.monto for t in query.filter(models.Transaccion.tipo == "ingreso").all())
    gastos = sum(t.monto for t in query.filter(models.Transaccion.tipo == "gasto").all())
    
    # Inversiones
    inversiones_activas = sum(t.monto for t in query.filter(
        models.Transaccion.tipo == "inversion",
        models.Transaccion.estado == "activa"
    ).all())
    retornos = sum(t.monto for t in query.filter(
        models.Transaccion.tipo == "retorno_inversion"
    ).all())
    
    # Créditos
    creditos = sum(t.monto for t in query.filter(
        models.Transaccion.tipo == "credito"
    ).all())
    pagos_creditos = sum(t.monto for t in query.filter(
        models.Transaccion.tipo == "pago_credito"
    ).all())
    creditos_pendientes = creditos - pagos_creditos
    
    # Cálculos finales
    balance_neto = ingresos - gastos + retornos - pagos_creditos
    patrimonio_neto = balance_neto + inversiones_activas - creditos_pendientes
    
    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "inversiones_activas": inversiones_activas,
        "retornos_inversiones": retornos,
        "creditos_pendientes": creditos_pendientes,
        "pagos_creditos": pagos_creditos,
        "balance_neto": balance_neto,
        "patrimonio_neto": patrimonio_neto
    }
@app.get("/transacciones/", response_model=List[schemas.Transaccion])
async def listar_transacciones(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    tipo: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    ordenar_por: Optional[str] = Query("fecha"),
    orden: Optional[str] = Query("desc"),
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == current_user.id
    )
    
    # Aplicar filtros
    if fecha_inicio:
        query = query.filter(models.Transaccion.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(models.Transaccion.fecha <= fecha_fin)
    if tipo:
        query = query.filter(models.Transaccion.tipo == tipo)
    if categoria:
        query = query.filter(models.Transaccion.categoria == categoria)
    
    # Aplicar ordenamiento
    if ordenar_por == "fecha":
        query = query.order_by(
            models.Transaccion.fecha.desc() if orden == "desc" 
            else models.Transaccion.fecha
        )
    elif ordenar_por == "monto":
        query = query.order_by(
            models.Transaccion.monto.desc() if orden == "desc" 
            else models.Transaccion.monto
        )
    
    return query.all()

@app.get("/transacciones/categorias/")
async def listar_categorias(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    categorias = db.query(models.Transaccion.categoria).distinct().filter(
        models.Transaccion.usuario_id == current_user.id
    ).all()
    return [cat[0] for cat in categorias]

@app.post("/inversiones/", response_model=schemas.Transaccion)
async def crear_inversion(
    inversion: schemas.TransaccionCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Validar datos de inversión
        if inversion.tipo != "inversion":
            raise HTTPException(status_code=400, detail="El tipo debe ser 'inversion'")
        
        # Crear la inversión
        datos_inversion = inversion.dict()
        datos_inversion["estado"] = "activa"
        datos_inversion["usuario_id"] = current_user.id
        
        nueva_inversion = models.Transaccion(**datos_inversion)
        
        db.add(nueva_inversion)
        db.commit()
        db.refresh(nueva_inversion)
        return nueva_inversion
        
    except Exception as e:
        db.rollback()
        print(f"Error al crear inversión: {str(e)}")  # Para debug
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inversiones/{inversion_id}/retorno", response_model=schemas.Transaccion)
async def registrar_retorno(
    inversion_id: int,
    retorno: schemas.RetornoCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que la inversión existe y pertenece al usuario
    inversion = db.query(models.Transaccion).filter(
        models.Transaccion.id == inversion_id,
        models.Transaccion.usuario_id == current_user.id,
        models.Transaccion.tipo == "inversion"
    ).first()
    
    if not inversion:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    
    # Crear el retorno
    db_retorno = models.Transaccion(
        tipo="retorno_inversion",
        monto=retorno.monto,
        fecha=retorno.fecha,
        descripcion=retorno.descripcion,
        categoria=retorno.categoria,
        usuario_id=current_user.id,
        inversion_relacionada_id=inversion_id
    )
    db.add(db_retorno)
    
    # Actualizar estado de la inversión si es necesario
    if retorno.fecha >= inversion.fecha_vencimiento:
        inversion.estado = "finalizada"
    
    db.commit()
    db.refresh(db_retorno)
    return db_retorno

@app.get("/inversiones/", response_model=List[schemas.Transaccion])
async def listar_inversiones(
    estado: Optional[str] = Query(None),
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == current_user.id,
        models.Transaccion.tipo == "inversion"
    )
    
    if estado:
        query = query.filter(models.Transaccion.estado == estado)
    
    return query.all()

@app.get("/inversiones/{inversion_id}/rendimiento")
async def calcular_rendimiento(
    inversion_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Obtener la inversión
    inversion = db.query(models.Transaccion).filter(
        models.Transaccion.id == inversion_id,
        models.Transaccion.usuario_id == current_user.id,
        models.Transaccion.tipo == "inversion"
    ).first()
    
    if not inversion:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    
    # Obtener todos los retornos
    retornos = db.query(models.Transaccion).filter(
        models.Transaccion.tipo == "retorno_inversion",
        models.Transaccion.inversion_relacionada_id == inversion_id
    ).all()
    
    total_retornos = sum(r.monto for r in retornos)
    rendimiento_porcentual = (total_retornos - inversion.monto) / inversion.monto * 100
    
    return {
        "inversion_inicial": inversion.monto,
        "total_retornos": total_retornos,
        "rendimiento_neto": total_retornos - inversion.monto,
        "rendimiento_porcentual": rendimiento_porcentual,
        "estado": inversion.estado,
        "fecha_inicio": inversion.fecha,
        "fecha_vencimiento": inversion.fecha_vencimiento
    }