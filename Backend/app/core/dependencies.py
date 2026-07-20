from fastapi import Depends
from app.core.database import SessionLocal
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