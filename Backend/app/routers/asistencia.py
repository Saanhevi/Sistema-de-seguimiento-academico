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

router = APIRouter(
    prefix="/asistencias",
    tags=["Asistencias"],
)

@router.get(
    "/cursos/{id_curso}",
    response_model=list[DiaAsistibleResponse]
)
def obtener_dias_asistencia(
    id_curso: int,
    service : 
):
    pass

@router.post(
    "/cursos/{id_curso}",
    response_model=DiaAsistibleResponse
)
def crear_dia_asistible(
    id_curso: int,
    request: CrearDiaAsistibleRequest,
):
    pass 

@router.get(
    "/{id_dia}",
    response_model=list[AsistenciaEstudianteResponse]
)
def obtener_asistencia(
    id_dia: int,
):
    pass

@router.put(
    "/{id_dia}",
    response_model=MensajeResponse
)
def registrar_asistencia(
    id_dia: int,
    request: list[AsistenciaEstudianteRequest],
):  
    pass

@router.get(
    "/estudiantes/{id_estudiante}",
    response_model=list[HistorialAsistenciaResponse]
)
def obtener_historial_asistencia(
    id_estudiante: int,
):
    pass