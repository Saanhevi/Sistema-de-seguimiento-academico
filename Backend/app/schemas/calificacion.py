from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# Postgres INTEGER (4 bytes) es el tipo de todas las columnas id_* de este módulo
ID_MAXIMO = 2_147_483_647


class SeccionPorcentajeCreate(BaseModel):
    nombre_seccion: str = Field(max_length=50)
    porcentaje: float
    id_curso: int = Field(gt=0, le=ID_MAXIMO)


class SeccionPorcentajeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_seccion: int
    nombre_seccion: str
    porcentaje: float
    id_curso: int
    advertencia: Optional[str] = None


class ActividadEvaluativaCreate(BaseModel):
    nombre: str = Field(max_length=50)
    fecha: date
    id_seccion: int = Field(gt=0, le=ID_MAXIMO)


class ActividadEvaluativaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_actividad: int
    nombre: str
    fecha: date
    id_seccion: int


class NotaCreate(BaseModel):
    id_actividad: int = Field(gt=0, le=ID_MAXIMO)
    id_estudiante: int = Field(gt=0, le=ID_MAXIMO)
    calificacion: float
    comentario: Optional[str] = Field(default=None, max_length=100)


class NotaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_nota: int
    id_actividad: int
    id_estudiante: int
    calificacion: float
    comentario: Optional[str] = None


class NotaCargaMasivaItem(BaseModel):
    id_estudiante: int = Field(gt=0, le=ID_MAXIMO)
    calificacion: float
    comentario: Optional[str] = Field(default=None, max_length=100)


class NotaCargaMasivaRequest(BaseModel):
    id_actividad: int = Field(gt=0, le=ID_MAXIMO)
    notas: list[NotaCargaMasivaItem]


class PromedioEstudianteResponse(BaseModel):
    """Una fila de HU8: el promedio ponderado de un estudiante en una materia.

    Solo lleva el id; el nombre lo resuelve quien ya tiene la lista de estudiantes
    del grado, para no repetir ese join en cada consulta de promedios.
    """

    id_estudiante: int
    promedio: float
