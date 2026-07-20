from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SeccionPorcentajeCreate(BaseModel):
    nombre_seccion: str
    porcentaje: float
    id_curso: int


class SeccionPorcentajeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_seccion: int
    nombre_seccion: str
    porcentaje: float
    id_curso: int


class ActividadEvaluativaCreate(BaseModel):
    nombre: str
    fecha: date
    id_seccion: int


class ActividadEvaluativaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_actividad: int
    nombre: str
    fecha: date
    id_seccion: int


class NotaCreate(BaseModel):
    id_actividad: int
    id_estudiante: int
    calificacion: float
    comentario: Optional[str] = None


class NotaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_nota: int
    id_actividad: int
    id_estudiante: int
    calificacion: float
    comentario: Optional[str] = None


class NotaCargaMasivaItem(BaseModel):
    id_estudiante: int
    calificacion: float
    comentario: Optional[str] = None


class NotaCargaMasivaRequest(BaseModel):
    id_actividad: int
    notas: list[NotaCargaMasivaItem]
