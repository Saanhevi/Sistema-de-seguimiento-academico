# Direccionamiento de las rutas de autenticación
from fastapi import APIRouter, Depends
from app.schemas.auth import LoginRequest, TokenResponse, CrearCuentaEstudiantilRequest, MensajeResponde, ActualizarPasswordRequest
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

@router.post("/estudiante", response_model=MensajeResponde)
def crear_cuenta_estudiantil(
    credentials: CrearCuentaEstudiantilRequest,
    service : AuthService = Depends(get_auth_service)
):
    return service.crear_cuenta_estudiantil(credentials)

@router.put("/estudiante/password", response_model=MensajeResponde)
def actualizar_contrasena(
    credentials : ActualizarPasswordRequest, 
    service : AuthService = Depends(get_auth_service)
):
    return service.actualizar_contrasena(credentials)