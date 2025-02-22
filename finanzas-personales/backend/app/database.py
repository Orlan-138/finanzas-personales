from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Usar URL con formato correcto para caracteres especiales
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Orlan_222-db@localhost:5432/finanzas_db"
).replace("\\", "")

# Crear el engine con parámetros adicionales
engine = create_engine(
    DATABASE_URL,
    client_encoding='utf8'
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()