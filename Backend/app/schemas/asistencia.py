from pydantic import BaseModel 
from datetime import date 

class CrearDiaAsistibleRequest(BaseModel):
    fecha: date

class DiaAsistibleResponse(BaseModel):
    id_dia: int
    fecha: date
    
class AsistenciaEstudianteRequest(BaseModel):
    id_estudiante: int
    estado: str
    
class AsistenciaEstudianteResponse(BaseModel):
    id_estudiante: int
    nombre: str
    estado: str | None
    
class HistorialAsistenciaResponse(BaseModel):
    curso: str
    fecha: date
    estado: str
    
class MensajeResponse(BaseModel):
    mensaje: str