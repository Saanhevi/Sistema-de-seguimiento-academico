from typing import Optional
from pydantic import BaseModel, ConfigDict


class GradoCreate(BaseModel):
    nombre: str


class GradoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_grado: int
    nombre: str


class MateriaCreate(BaseModel):
    nombre: str


class MateriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_materia: int
    nombre: str


class PeriodoAcademicoCreate(BaseModel):
    nombre: str
    anio: int
    estado: str


class PeriodoAcademicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_periodo: int
    nombre: str
    anio: int
    estado: str


class CursoCreate(BaseModel):
    id_docente: int
    id_grado: int
    id_materia: int
    id_periodo: int


class CursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_curso: int
    id_docente: int
    id_grado: int
    id_materia: int
    id_periodo: int
    # Anidados opcionales: Pydantic los lee de los relationship() del modelo Curso.
    # Evitan que el cliente tenga que cruzar /api/grados, /api/materias y /api/periodos.
    grado: Optional[GradoResponse] = None
    materia: Optional[MateriaResponse] = None
    periodo: Optional[PeriodoAcademicoResponse] = None


class MatriculaCreate(BaseModel):
    id_estudiante: int
    id_grado: int
    anio: int


class MatriculaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_matricula: int
    id_estudiante: int
    id_grado: int
    anio: int


class EstudianteMatriculadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_estudiante: int
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
