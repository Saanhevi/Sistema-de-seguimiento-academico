from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, model_validator


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


class DocenteCursoResponse(BaseModel):
    """Docente tal como se muestra dentro de un curso (HU10: 'la materia, el profesor').

    Nombre distinto al de `app.schemas.docente.DocenteResponse`, que es otra forma
    (`id`/`nombres`/`apellidos`/`correo`/`estado`) usada por el módulo de profesores.
    """

    model_config = ConfigDict(from_attributes=True)

    id_docente: int
    # Opcionales a propósito (RN-10d): un docente sin fila Usuario degrada a null
    # en vez de tumbar con un 500 la lista entera de cursos.
    nombre: Optional[str] = None
    apellido: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _aplanar_usuario(cls, data: Any) -> Any:
        # nombre/apellido viven en Usuario, no en Docente. Se aplanan aquí y no con
        # un @property en el modelo ORM, que el query layer no puede usar.
        if isinstance(data, dict):
            return data

        usuario = getattr(data, "usuario", None)
        return {
            "id_docente": getattr(data, "id_docente", None),
            "nombre": getattr(usuario, "nombres", None),
            "apellido": getattr(usuario, "apellidos", None),
        }


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
    docente: Optional[DocenteCursoResponse] = None


class CursoDocenteResponse(BaseModel):
    id_curso: int
    id_docente: int
    id_grado: int
    id_materia: int
    id_periodo: int
    grado: str
    materia: str
    periodo: str
    anio: int


class CursoEstudianteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_estudiante: int
    nombres: str
    apellidos: str
    correo: Optional[str] = None
    asociado: bool = False


class CursoEstudiantesResponse(BaseModel):
    id_curso: int
    grado: str
    materia: str
    periodo: str
    anio: int
    estudiantes_disponibles: list[CursoEstudianteResponse]
    estudiantes_asociados: list[CursoEstudianteResponse]


class CursoEstudianteAsignarRequest(BaseModel):
    id_estudiante: int


class CursoEstudianteAsignadoResponse(BaseModel):
    mensaje: str
    curso: CursoDocenteResponse
    estudiante: CursoEstudianteResponse


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
    # HU22: null para los usuarios creados antes de que existiera la columna.
    documento: Optional[str] = None