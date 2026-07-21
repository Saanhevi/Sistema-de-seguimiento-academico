from fastapi import APIRouter, Depends
from app.services.asistencia import AsistenciaService

from app.schemas.asistencia import (
    CrearDiaAsistibleRequest,
    DiaAsistibleResponse,
    AsistenciaEstudianteRequest,
    AsistenciaEstudianteResponse,
    HistorialAsistenciaResponse,
    MensajeResponse,
)

# TODO: Completar la implementación real de estos endpoints y conectar el router con el servicio y el RBAC.
router = APIRouter(
    prefix="/asistencias",
    tags=["Asistencias"],
)

# @router.get(
#     "/cursos/{id_curso}",
#     response_model=list[DiaAsistibleResponse]
# )
# def obtener_dias_asistencia(
#     id_curso: int,
#     service : 
# ):
#     pass

# TODO: Implementar este endpoint con validación de autorización y persistencia real.
@router.post(
    "/cursos/{id_curso}",
    response_model=DiaAsistibleResponse
)
def crear_dia_asistible(
    id_curso: int,
    request: CrearDiaAsistibleRequest,
):
    pass 

# TODO: Implementar la consulta de asistencia por día y definir el contrato de respuesta real.
@router.get(
    "/{id_dia}",
    response_model=list[AsistenciaEstudianteResponse]
)
def obtener_asistencia(
    id_dia: int,
):
    pass

# TODO: Implementar la actualización de asistencia con manejo de estados y permisos.
@router.put(
    "/{id_dia}",
    response_model=MensajeResponse
)
def registrar_asistencia(
    id_dia: int,
    request: list[AsistenciaEstudianteRequest],
):  
    pass

# TODO: Implementar el historial de asistencia con filtros y datos reales del estudiante.
@router.get(
    "/estudiantes/{id_estudiante}",
    response_model=list[HistorialAsistenciaResponse]
)
def obtener_historial_asistencia(
    id_estudiante: int,
):
    pass