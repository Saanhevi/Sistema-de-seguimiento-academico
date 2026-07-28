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


# --- HU22: importación desde Excel ---
# La previsualización no escribe nada (RN-q): estos esquemas describen un
# reporte, no un cambio. La escritura sigue siendo NotaCargaMasivaRequest.


class ImportacionFilaValida(BaseModel):
    """Una fila del archivo que ya quedó resuelta a un estudiante del curso."""

    # Número de fila tal como lo ve Excel (encabezado = 1, primer dato = 2).
    fila: int
    id_estudiante: int
    calificacion: float
    comentario: Optional[str] = None
    # Solo para pintar la vista previa; el paso de confirmación los descarta.
    nombre: Optional[str] = None
    apellido: Optional[str] = None


class ImportacionErrorFila(BaseModel):
    """Un problema ubicable: fila de Excel, columna, valor y qué hacer."""

    fila: int
    columna: str
    valor: Optional[str] = None
    mensaje: str


class ImportacionEstudianteSinNota(BaseModel):
    """RN-u: matriculado al que el archivo no menciona y que sigue sin nota."""

    id_estudiante: int
    nombre: Optional[str] = None
    apellido: Optional[str] = None


class ImportacionNotasResponse(BaseModel):
    id_actividad: int
    # El nombre viaja para que el frontend pueda confirmar el destino en el
    # propio botón de guardar (RN-w): el archivo no lleva id_actividad.
    actividad: str
    total_filas: int
    filas_validas: list[ImportacionFilaValida]
    filas_omitidas: int  # RN-l: sin calificación
    errores: list[ImportacionErrorFila]
    estudiantes_sin_nota: list[ImportacionEstudianteSinNota]
