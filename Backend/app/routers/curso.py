from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_curso_service, get_session, require_role
from app.schemas.curso import (
    CursoCreate,
    CursoResponse,
    EstudianteMatriculadoResponse,
    GradoCreate,
    GradoResponse,
    MateriaCreate,
    MateriaResponse,
    MatriculaCreate,
    MatriculaResponse,
    PeriodoAcademicoCreate,
    PeriodoAcademicoResponse,
)
from app.services.curso import CursoService

router = APIRouter(prefix="/api", tags=["Cursos", "Grados", "Materias", "Periodos", "Matrículas"])


@router.post("/grados", response_model=GradoResponse)
def crear_grado(
    payload: GradoCreate,
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador")),
):
    return service.crear_grado(payload.nombre)


@router.get("/grados", response_model=list[GradoResponse])
def listar_grados(
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_grados()


@router.post("/materias", response_model=MateriaResponse)
def crear_materia(
    payload: MateriaCreate,
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador")),
):
    return service.crear_materia(payload.nombre)


@router.get("/materias", response_model=list[MateriaResponse])
def listar_materias(
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_materias()


@router.post("/periodos", response_model=PeriodoAcademicoResponse)
def crear_periodo(
    payload: PeriodoAcademicoCreate,
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador")),
):
    return service.crear_periodo(payload.nombre, payload.anio, payload.estado)


@router.get("/periodos", response_model=list[PeriodoAcademicoResponse])
def listar_periodos(
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_periodos()


@router.post("/cursos", response_model=CursoResponse)
def crear_curso(
    payload: CursoCreate,
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    return service.crear_curso(payload.id_docente, payload.id_grado, payload.id_materia, payload.id_periodo, usuario_actual=usuario)


@router.get("/cursos", response_model=list[CursoResponse])
def listar_cursos(
    id_docente: int | None = None,
    id_grado: int | None = None,
    id_periodo: int | None = None,
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_cursos(id_docente=id_docente, id_grado=id_grado, id_periodo=id_periodo)


@router.get("/cursos/{id_curso}", response_model=CursoResponse)
def obtener_curso(
    id_curso: int,
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.obtener_curso(id_curso)


@router.post("/matriculas", response_model=MatriculaResponse)
def crear_matricula(
    payload: MatriculaCreate,
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    return service.crear_matricula(payload.id_estudiante, payload.id_grado, payload.anio, usuario_actual=usuario)


@router.get("/matriculas", response_model=list[MatriculaResponse])
def listar_matriculas(
    id_grado: int | None = None,
    anio: int | None = None,
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_matriculas(id_grado=id_grado, anio=anio)


@router.get("/grados/{id_grado}/estudiantes", response_model=list[EstudianteMatriculadoResponse])
def listar_estudiantes_del_grado(
    id_grado: int,
    anio: int | None = Query(default=None),
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_estudiantes_por_grado(id_grado=id_grado, anio=anio)
