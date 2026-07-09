# Direccionamiento de las rutas de autenticación
from fastapi import APIRouter
from app.schemas.auth import LoginRequest
from app.services import auth as auth_service

router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)

@router.post("/login")
def login(credentials: LoginRequest):
    #pasamos las credenciales a servicio para que se verifiquen allí
    return auth_service.credentials_verification(credentials)