# Direccionamiento de las rutas de autenticación
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth as auth_service
from app.core.database import SessionLocal # Fábrica de sesiones

router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)

# Dependencia de FastAPI: Abre y cierra la conexión con PostgreSQL
def get_db():
    db = SessionLocal() # Abre una conexión limpia usando el motor
    try:
        yield db        # Le entrega la conexión a la ruta que la solicitó
    finally:
        db.close()      # Cuando la ruta termina su trabajo, cierra la conexión pase lo que pase


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    #pasamos las credenciales a servicio para que se verifiquen allí
    return auth_service.autenticar_usuario(credentials, db)