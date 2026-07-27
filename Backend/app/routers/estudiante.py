from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_session, require_role
from app.schemas.estudiante import EstudianteResponse
from app.services.estudiante import EstudianteService

router = APIRouter(prefix="/api/estudiantes", tags=["Estudiantes"])


def get_estudiante_service(session=Depends(get_session)):
    return EstudianteService(session)


@router.get("", response_model=list[EstudianteResponse])
def listar_estudiantes(
    incluir_inactivos: bool = Query(default=True),
    service: EstudianteService = Depends(get_estudiante_service),
    usuario=Depends(require_role("Administrador")),
):
    return service.listar(incluir_inactivos=incluir_inactivos)


@router.patch("/{id_estudiante}/retiro", response_model=EstudianteResponse)
def retirar_estudiante(
    id_estudiante: int,
    service: EstudianteService = Depends(get_estudiante_service),
    usuario=Depends(require_role("Administrador")),
):
    return service.retirar(id_estudiante)
