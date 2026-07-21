from fastapi import APIRouter, Depends

from app.core.dependencies import get_session, require_role
from app.schemas.docente import DocenteCreate, DocenteEstadoUpdate, DocenteResponse, DocenteUpdate
from app.services.docente import DocenteService

router = APIRouter(prefix="/api/docentes", tags=["Docentes"])


def get_docente_service(session=Depends(get_session)):
    return DocenteService(session)


@router.get("", response_model=list[DocenteResponse])
def listar_docentes(
    service: DocenteService = Depends(get_docente_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar()


@router.post("", response_model=DocenteResponse)
def crear_docente(
    payload: DocenteCreate,
    service: DocenteService = Depends(get_docente_service),
    usuario=Depends(require_role("Administrador")),
):
    return service.crear(payload.model_dump())


@router.put("/{id_docente}", response_model=DocenteResponse)
def actualizar_docente(
    id_docente: int,
    payload: DocenteUpdate,
    service: DocenteService = Depends(get_docente_service),
    usuario=Depends(require_role("Administrador")),
):
    return service.actualizar(id_docente, payload.model_dump(exclude_unset=True))


@router.patch("/{id_docente}/estado", response_model=DocenteResponse)
def cambiar_estado_docente(
    id_docente: int,
    payload: DocenteEstadoUpdate,
    service: DocenteService = Depends(get_docente_service),
    usuario=Depends(require_role("Administrador")),
):
    return service.cambiar_estado(id_docente, payload.estado)
