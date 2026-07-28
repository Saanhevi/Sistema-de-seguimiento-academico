from pydantic import BaseModel 
from datetime import date 
from typing import Literal

EstadoAsistencia = Literal["Presente", "Ausente", "Retardo", "Excusa"] 

#Necesarios para mostrar la lista de asistencias
class AsistenciaResponse(BaseModel):
    id_estudiante: int 
    nombres : str 
    apellidos : str 
    estado : EstadoAsistencia 
    
class AsistenciaListaResponse(BaseModel):
    id_dia: int 
    grado: str 
    materia: str 
    fecha : date 
    asistencias : list[AsistenciaResponse]
    

# Clase para guardar la asistencia de un estudiante
class AsistenciaRequest(BaseModel):
    id_estudiante : int 
    estado : EstadoAsistencia 

# Clase para mostrar asistencias al estudiante
class AsistenciaEstudianteResponse(BaseModel):
    materia : str 
    fecha : date 
    estado : EstadoAsistencia 

# Mensaje sobre la asistencia
class AsistenciaMensajeResponse(BaseModel):
    mensaje: str 
    
#Dia en donde se toma asistencia
class DiaAsistibleResponse(BaseModel):
    fecha : date
    
    