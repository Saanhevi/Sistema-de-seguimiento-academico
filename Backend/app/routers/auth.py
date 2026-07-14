# Direccionamiento de las rutas de autenticación
from fastapi import APIRouter, Depends
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import AuthService
from app.core.dependencies import get_auth_service
router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, service : AuthService = Depends(get_auth_service) ):
    #pasamos las credenciales a servicio para que se verifiquen allí
    return service.autenticar_usuario(credentials)