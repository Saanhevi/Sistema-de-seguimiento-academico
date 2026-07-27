from pydantic import BaseModel 
from datetime import date 

#Necesarios para mostrar la lista de asistencias
class AsistenciaResponse(BaseModel):
    id_estudiante: int 
    nombres : str 
    apellidos : str 
    estado : str 
    
class AsistenciaListaResponse(BaseModel):
    id_dia: int 
    grado: str 
    materia: str 
    fecha : date 
    asistencias : list[AsistenciaResponse]
    

# Clase para guardar la asistencia de un estudiante
class AsistenciaRequest(BaseModel):
    id_estudiante : int 
    estado : str 

# Clase para mostrar asistencias al estudiante
class AsistenciaEstudianteResponse(BaseModel):
    materia : str 
    fecha : date 
    estado : str 

# Mensaje sobre la asistencia
class AsistenciaMensajeResponse(BaseModel):
    mensaje: str 
    
#Dia en donde se toma asistencia
class DiaAsistibleResponse(BaseModel):
    fecha : date
    
    