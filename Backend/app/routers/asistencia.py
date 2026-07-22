from fastapi import APIRouter, Depends, Query
from app.services.asistencia import AsistenciaService
from app.core.dependencies import get_asistencia_service
from app.schemas.asistencia import (
    AsistenciaListaResponse,
    DiaAsistibleResponse,
    AsistenciaRequest,
    AsistenciaEstudianteResponse,
    AsistenciaMensajeResponse
)
from datetime import date 

router = APIRouter(
    prefix="/asistencias",
    tags=["Asistencias"],
)

@router.get("/listas" , response_model=AsistenciaListaResponse)
def obtener_lista_asistencias(
    service : AsistenciaService = Depends(get_asistencia_service),
    id_curso : int = Query(..., description="ID del Curso"),
    fecha : date = Query(..., description="Fecha donde se toma asistencia")
):
    return 

@router.put("/listas/{id_dia}", response_model=AsistenciaMensajeResponse)
def guardar_asistencia(
    lista_asistencia : list[AsistenciaRequest],
    id_dia : int,
    service : AsistenciaService = Depends(get_asistencia_service)
):
    return 

@router.get("/mis-asistencias", response_model=list[AsistenciaEstudianteResponse])
def consultar_mis_asistencias(
    service : AsistenciaService = Depends(get_asistencia_service)
):
    return 

@router.get("/listas/{id_curso}", response_model=list[DiaAsistibleResponse])
def consultar_historial_dias(
    id_curso : int,
    service : AsistenciaService = Depends(get_asistencia_service),
): 
    return 