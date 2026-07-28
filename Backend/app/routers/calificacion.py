from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.core.dependencies import get_calificacion_service, require_role
from app.schemas.calificacion import (
    ID_MAXIMO,
    ActividadEvaluativaCreate,
    ActividadEvaluativaResponse,
    NotaCargaMasivaRequest,
    NotaCreate,
    NotaResponse,
    PromedioEstudianteResponse,
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
    id_actividad: int = Path(..., gt=0, le=ID_MAXIMO),
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    service.eliminar_actividad(id_actividad, usuario)
    return None


@router.delete("/secciones/{id_seccion}", status_code=204)
def eliminar_seccion(
    id_seccion: int = Path(..., gt=0, le=ID_MAXIMO),
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
    # PUT tiene semántica de actualización explícita: solo modifica notas existentes.
    return service.actualizar_nota(payload.id_actividad, payload.id_estudiante, payload.calificacion, payload.comentario, usuario)


@router.get("/notas", response_model=list[NotaResponse])
def listar_notas(
    id_actividad: int | None = Query(default=None, gt=0, le=ID_MAXIMO),
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_notas(id_actividad=id_actividad, usuario=usuario)
@router.get("/notas/promedio")
def obtener_promedio_estudiante_materia(
    id_estudiante: int = Query(..., gt=0, le=ID_MAXIMO),
    id_materia: int = Query(..., gt=0, le=ID_MAXIMO),
    id_periodo: int = Query(..., gt=0, le=ID_MAXIMO), 
    service: CalificacionService = Depends(get_calificacion_service),
    usuario = Depends(require_role("Administrador", "Docente", "Estudiante"))
):
   
    if usuario.rol == "Estudiante" and usuario.id_usuario != id_estudiante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para consultar el promedio de otro estudiante."
        )


    # El servicio acota al Docente a sus propios cursos (RN-03).
    promedio = service.obtener_promedio_estudiante_materia(id_estudiante, id_materia, id_periodo, usuario)

    return {
        "id_estudiante": id_estudiante,
        "id_materia": id_materia,
        "id_periodo": id_periodo,
        "promedio": promedio
    }


@router.get(
    "/materia/{id_materia}/promedios-estudiantes",
    response_model=list[PromedioEstudianteResponse],
    summary="Promedio de cada estudiante en una materia (HU8)",
)
def listar_promedios_estudiantes_materia(
    id_materia: int = Path(..., gt=0, le=ID_MAXIMO),
    id_periodo: int = Query(..., gt=0, le=ID_MAXIMO),
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    promedios = service.obtener_promedios_por_estudiante_materia(id_materia, usuario, id_periodo)

    # Orden estable por id: la tabla del docente se cruza con la lista de estudiantes
    # del grado, que ya viene ordenada por el backend.
    return [
        PromedioEstudianteResponse(id_estudiante=id_estudiante, promedio=promedio)
        for id_estudiante, promedio in sorted(promedios.items())
    ]


@router.get("/materia/{id_materia}/promedio-grupal", summary="Obtener promedio grupal de una materia (HU9)")
def obtener_promedio_grupal_materia(
    id_materia: int = Path(..., gt=0, le=ID_MAXIMO),
    id_periodo: int = Query(..., gt=0, le=ID_MAXIMO),
    service: CalificacionService = Depends(get_calificacion_service),
    usuario = Depends(require_role("Administrador", "Docente")),
):

    promedio = service.obtener_promedio_grupal_materia(id_materia, usuario, id_periodo)

    return {
        "id_materia": id_materia,
        "id_periodo": id_periodo,
        "promedio_grupal": promedio
    }