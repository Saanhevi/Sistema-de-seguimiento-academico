from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase


# Se crea el motor de conexion
engine = create_engine(settings.DATABASE_URL, echo =False) # Para debbuguear dejar echo = True

# Se crea la fabrica de sesiones
SessionLocal = sessionmaker(bind=engine)

# Se crea la clase Base que heredaran todas las tablas ORM
class Base(DeclarativeBase):
    pass 



