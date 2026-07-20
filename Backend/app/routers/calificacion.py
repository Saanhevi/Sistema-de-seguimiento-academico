from fastapi import APIRouter, Depends
from app.core.dependencies import get_calificacion_service, require_role
from app.schemas.calificacion import (
    ActividadEvaluativaCreate,
    ActividadEvaluativaResponse,
    NotaCargaMasivaRequest,
    NotaCreate,
    NotaResponse,
    SeccionPorcentajeCreate,
    SeccionPorcentajeResponse,
)
from app.services.calificacion import CalificacionService

router = APIRouter(prefix="/api", tags=["Calificaciones"])


@router.post("/secciones", response_model=SeccionPorcentajeResponse)
def crear_seccion(
    payload: SeccionPorcentajeCreate,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    return service.crear_seccion(payload.nombre_seccion, payload.porcentaje, payload.id_curso)


@router.get("/secciones", response_model=list[SeccionPorcentajeResponse])
def listar_secciones(
    id_curso: int | None = None,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_secciones(id_curso=id_curso)


@router.post("/actividades", response_model=ActividadEvaluativaResponse)
def crear_actividad(
    payload: ActividadEvaluativaCreate,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    return service.crear_actividad(payload.nombre, payload.fecha, payload.id_seccion)


@router.get("/actividades", response_model=list[ActividadEvaluativaResponse])
def listar_actividades(
    id_seccion: int | None = None,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_actividades(id_seccion=id_seccion)


@router.post("/notas/carga-masiva", response_model=list[NotaResponse])
def cargar_notas_masivo(
    payload: NotaCargaMasivaRequest,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    notas = [item.model_dump() for item in payload.notas]
    return service.cargar_notas_masivo(payload.id_actividad, notas)


@router.post("/notas", response_model=NotaResponse)
def crear_nota(
    payload: NotaCreate,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    return service.crear_nota(payload.id_actividad, payload.id_estudiante, payload.calificacion, payload.comentario)


@router.get("/notas", response_model=list[NotaResponse])
def listar_notas(
    id_actividad: int | None = None,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_notas(id_actividad=id_actividad)
