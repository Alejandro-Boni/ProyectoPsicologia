from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carga la configuración del archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Crea el motor de conexión
engine = create_engine(DATABASE_URL)

# Crea una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para crear nuestras tablas (Psicólogos, Pacientes, etc.)
Base = declarative_base()