from pydantic import BaseModel 
from datetime import date 

# TODO: Definir validaciones reales para fechas, estados y contratos de respuesta del módulo de asistencia.
class CrearDiaAsistibleRequest(BaseModel):
    fecha: date

# TODO: Incluir los campos del dominio real en la respuesta del día asistible.
class DiaAsistibleResponse(BaseModel):
    id_dia: int
    fecha: date
    
class AsistenciaEstudianteRequest(BaseModel):
    id_estudiante: int
    estado: str
    
# TODO: Definir un enum o validación para los estados de asistencia.
class AsistenciaEstudianteResponse(BaseModel):
    id_estudiante: int
    nombre: str
    estado: str | None
    
# TODO: Completar la forma del historial con los campos requeridos por el frontend.
class HistorialAsistenciaResponse(BaseModel):
    curso: str
    fecha: date
    estado: str
    
class MensajeResponse(BaseModel):
    mensaje: str