from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_calificacion_service, require_role
from app.schemas.calificacion import (
    ID_MAXIMO,
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
    return service.crear_seccion(payload.nombre_seccion, payload.porcentaje, payload.id_curso, usuario)


@router.get("/secciones", response_model=list[SeccionPorcentajeResponse])
def listar_secciones(
    id_curso: int | None = Query(default=None, gt=0, le=ID_MAXIMO),
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_secciones(id_curso=id_curso, usuario=usuario)


@router.post("/actividades", response_model=ActividadEvaluativaResponse)
def crear_actividad(
    payload: ActividadEvaluativaCreate,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    return service.crear_actividad(payload.nombre, payload.fecha, payload.id_seccion, usuario)


@router.get("/actividades", response_model=list[ActividadEvaluativaResponse])
def listar_actividades(
    id_seccion: int | None = Query(default=None, gt=0, le=ID_MAXIMO),
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_actividades(id_seccion=id_seccion, usuario=usuario)


@router.delete("/actividades/{id_actividad}", status_code=204)
def eliminar_actividad(
    id_actividad: int,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    service.eliminar_actividad(id_actividad, usuario)
    return None


@router.delete("/secciones/{id_seccion}", status_code=204)
def eliminar_seccion(
    id_seccion: int,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    service.eliminar_seccion(id_seccion, usuario)
    return None


@router.post("/notas/carga-masiva", response_model=list[NotaResponse])
def cargar_notas_masivo(
    payload: NotaCargaMasivaRequest,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    notas = [item.model_dump() for item in payload.notas]
    return service.cargar_notas_masivo(payload.id_actividad, notas, usuario)


@router.post("/notas", response_model=NotaResponse)
def crear_nota(
    payload: NotaCreate,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    return service.crear_nota(payload.id_actividad, payload.id_estudiante, payload.calificacion, payload.comentario, usuario)


@router.put("/notas", response_model=NotaResponse)
def actualizar_nota(
    payload: NotaCreate,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    # Reutilizamos crear_nota como upsert validado (ver reglas RN-*)
    return service.crear_nota(payload.id_actividad, payload.id_estudiante, payload.calificacion, payload.comentario, usuario)


@router.get("/notas", response_model=list[NotaResponse])
def listar_notas(
    id_actividad: int | None = Query(default=None, gt=0, le=ID_MAXIMO),
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_notas(id_actividad=id_actividad, usuario=usuario)
@router.get( "/notas/promedio", dependencies=[Depends(require_role("Administrador", "Docente", "Estudiante"))]
)
def obtener_promedio_estudiante_materia(
    id_estudiante: int = Query(..., gt=0, le=ID_MAXIMO),
    id_materia: int = Query(..., gt=0, le=ID_MAXIMO),
    service: CalificacionService = Depends(get_calificacion_service),
):
    #Retorna el promedio de notas de un estudiante en una materia específica.
    
    promedio = service.obtener_promedio_estudiante_materia(id_estudiante, id_materia)
    return {
        "id_estudiante": id_estudiante,
        "id_materia": id_materia,
        "promedio": promedio
    }
@router.get("/materia/{id_materia}/promedio-grupal", summary="Obtener promedio grupal de una materia")
def obtener_promedio_grupal_materia(
    id_materia: int,
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
    ):
    #Calcula el promedio general de todos los estudiantes en una materia específica,basado en los cursos que dicta el docente autenticado.
   
    promedio = service.obtener_promedio_grupal_materia(id_materia, usuario)
    return {"id_materia": id_materia, "promedio_grupal": promedio}