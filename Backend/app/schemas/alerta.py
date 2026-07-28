from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

ID_MAXIMO = 2_147_483_647


class AlertaCreate(BaseModel):
    id_estudiante: int = Field(gt=0, le=ID_MAXIMO)
    id_curso: Optional[int] = Field(default=None, gt=0, le=ID_MAXIMO)
    tipo: str = Field(max_length=100)
    mensaje: str = Field(max_length=200)
    nivel: str = Field(max_length=10)


class AlertaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_alerta: int
    id_estudiante: int
    id_curso: Optional[int] = None
    tipo: str
    mensaje: str
    nivel: str
    fecha: datetime
    estado: str
    nombre_estudiante: Optional[str] = None
    nombre_curso: Optional[str] = None
