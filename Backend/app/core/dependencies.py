import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.repositories.usuario import UsuarioRepository
from app.services.auth import AuthService
from app.services.curso import CursoService

# Obtener una session
def get_session():
    return SessionLocal()

# Obtener un servicio
def get_auth_service(session = Depends(get_session)):
    repositorio = UsuarioRepository(session)
    return AuthService(session, repositorio)


def get_curso_service(session = Depends(get_session)):
    return CursoService(session)

# Esquema de autenticación: espera un header "Authorization: Bearer <token>"
security_scheme = HTTPBearer()

def get_current_user(
    credenciales: HTTPAuthorizationCredentials = Depends(security_scheme),
    session = Depends(get_session),
):
    """
    Decodifica el token del header Authorization, busca al Usuario dueño del
    claim "sub" y valida que siga activo (si su rol es Docente o Estudiante).
    Retorna el objeto Usuario. Lanza HTTPException 401 si el token es
    inválido/expiró, el usuario no existe, o está inactivo.
    """
    # 1. Decodificamos el token, traduciendo los errores de jwt a 401
    try:
        payload = decode_access_token(credenciales.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    # 2. Extraemos el id_usuario del claim "sub"
    try:
        id_usuario = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: identificador de usuario malformado"
        )

    # 3. Buscamos al usuario reutilizando el repositorio existente
    repositorio = UsuarioRepository(session)
    usuario = repositorio.buscar_por_id(id_usuario)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario del token ya no existe"
        )

    # 4. Si el usuario es Docente o Estudiante, confirmamos que siga activo:
    # el colegio puede desactivarlo y su token viejo seguiría vigente hasta expirar
    if usuario.rol == "Docente":
        if usuario.rol_docente is None or usuario.rol_docente.estado != "Activo":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El usuario está inactivo"
            )

    if usuario.rol == "Estudiante":
        if usuario.rol_estudiante is None or usuario.rol_estudiante.estado != "Activo":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El usuario está inactivo"
            )

    return usuario

def require_role(*roles_permitidos: str):
    """
    Dependency factory para proteger endpoints por rol. Uso en otro router:
        Depends(require_role("Administrador", "Docente"))
    Lanza HTTPException 403 si el rol del usuario actual no está en roles_permitidos.
    """
    def _verificar(usuario = Depends(get_current_user)):
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para esta acción"
            )
        return usuario
    return _verificar
