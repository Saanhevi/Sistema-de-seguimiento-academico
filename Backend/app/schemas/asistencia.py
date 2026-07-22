from pydantic import BaseModel 
from datetime import date 

#Necesarios para mostrar la lista de asistencias
class AsistenciaListaResponse(BaseModel):
    id_dia: int 
    grado: str 
    materia: str 
    fecha : date 
    asistencias : list[AsistenciaResponse]
    
class AsistenciaResponse(BaseModel):
    id_estudiante: int 
    nombres : str 
    apellidos : str 
    estado : str 
    
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
    
    
    