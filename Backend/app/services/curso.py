from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curso import Curso
from app.models.grado import Grado
from app.models.materia import Materia
from app.models.periodo_academico import PeriodoAcademico
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.models.matricula import Matricula
from app.models.usuario import Usuario
from app.repositories.curso import CursoRepository
from app.repositories.grado import GradoRepository
from app.repositories.materia import MateriaRepository
from app.repositories.periodo_academico import PeriodoAcademicoRepository
from app.repositories.matricula import MatriculaRepository


class CursoService:

    asociaciones_curso_estudiante: set[tuple[int, int]] = set()

    def __init__(self, session: Session):
        self.session = session
        self.grado_repo = GradoRepository(session)
        self.materia_repo = MateriaRepository(session)
        self.periodo_repo = PeriodoAcademicoRepository(session)
        self.curso_repo = CursoRepository(session)
        self.matricula_repo = MatriculaRepository(session)

    def _validar_nombre(self, nombre: str, campo: str) -> str:
        nombre_limpio = (nombre or "").strip()
        if not nombre_limpio:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El {campo} no puede estar vacío")
        return nombre_limpio

    def _validar_anio(self, anio: int) -> int:
        if not isinstance(anio, int) or isinstance(anio, bool):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El año debe ser un número entero")
        if anio <= 0 or anio > 2100:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El año no es válido")
        return anio

    def _obtener_curso_validado(self, id_curso: int, usuario_actual=None) -> Curso:
        curso = self.curso_repo.buscar_por_id(id_curso)
        if not curso:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

        if usuario_actual is not None and usuario_actual.rol == "Docente" and curso.id_docente != usuario_actual.id_usuario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para gestionar este curso")

        return curso

    def _obtener_anio_curso(self, curso: Curso) -> int:
        if curso.periodo and getattr(curso.periodo, "anio", None):
            return int(curso.periodo.anio)
        return date.today().year

    def _serializar_curso_docente(self, curso: Curso) -> dict:
        return {
            "id_curso": curso.id_curso,
            "id_docente": curso.id_docente,
            "id_grado": curso.id_grado,
            "id_materia": curso.id_materia,
            "id_periodo": curso.id_periodo,
            "grado": curso.grado.nombre,
            "materia": curso.materia.nombre,
            "periodo": curso.periodo.nombre,
            "anio": self._obtener_anio_curso(curso),
        }

    def _obtener_estudiantes_matriculados_del_curso(self, curso: Curso) -> list[dict]:
        anio_curso = self._obtener_anio_curso(curso)
        query = (
            select(
                Matricula.id_estudiante,
                Usuario.nombres,
                Usuario.apellidos,
                Usuario.correo,
            )
            .join(Estudiante, Estudiante.id_estudiante == Matricula.id_estudiante)
            .join(Usuario, Usuario.id_usuario == Estudiante.id_estudiante)
            .where(
                Matricula.id_grado == curso.id_grado,
                Matricula.anio == anio_curso,
            )
        )

        rows = self.session.execute(query).all()
        estudiantes = []

        for row in rows:
            asociado = (curso.id_curso, row.id_estudiante) in self.asociaciones_curso_estudiante
            estudiantes.append({
                "id_estudiante": row.id_estudiante,
                "nombres": row.nombres,
                "apellidos": row.apellidos,
                "correo": row.correo,
                "asociado": asociado,
            })

        return estudiantes

    def crear_grado(self, nombre: str) -> Grado:
        nombre_limpio = self._validar_nombre(nombre, "nombre del grado")

        grado = Grado(nombre=nombre_limpio)
        return self.grado_repo.crear(grado)

    def listar_grados(self) -> list[Grado]:
        return self.grado_repo.listar()

    def crear_materia(self, nombre: str) -> Materia:
        nombre_limpio = self._validar_nombre(nombre, "nombre de la materia")

        materia = Materia(nombre=nombre_limpio)
        return self.materia_repo.crear(materia)

    def listar_materias(self) -> list[Materia]:
        return self.materia_repo.listar()

    def crear_periodo(self, nombre: str, anio: int, estado: str) -> PeriodoAcademico:
        nombre_limpio = self._validar_nombre(nombre, "nombre del periodo")
        anio_valido = self._validar_anio(anio)
        if estado not in {"Abierto", "Cerrado"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El estado debe ser Abierto o Cerrado")

        periodo = PeriodoAcademico(nombre=nombre_limpio, anio=anio_valido, estado=estado)
        return self.periodo_repo.crear(periodo)

    def listar_periodos(self) -> list[PeriodoAcademico]:
        return self.periodo_repo.listar()

    def crear_curso(self, id_docente: int, id_grado: int, id_materia: int, id_periodo: int, usuario_actual=None) -> Curso:
        if usuario_actual is not None and usuario_actual.rol == "Docente" and usuario_actual.id_usuario != id_docente:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para asignar un curso a otro docente")

        docente = self.session.get(Docente, id_docente)
        if not docente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")

        grado = self.grado_repo.buscar_por_id(id_grado)
        if not grado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grado no encontrado")

        materia = self.materia_repo.buscar_por_id(id_materia)
        if not materia:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")

        periodo = self.periodo_repo.buscar_por_id(id_periodo)
        if not periodo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo académico no encontrado")

        usuario_docente = self.session.get(Usuario, id_docente)
        if usuario_docente is None or getattr(usuario_docente, "rol", None) != "Docente":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El docente debe existir y tener rol Docente")

        curso_existente = self.curso_repo.buscar_por_combinacion(id_docente, id_grado, id_materia, id_periodo)
        if curso_existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El curso ya existe")

        curso = Curso(
            id_docente=id_docente,
            id_grado=id_grado,
            id_materia=id_materia,
            id_periodo=id_periodo,
        )
        return self.curso_repo.crear(curso)

    def listar_cursos(self, id_docente=None, id_grado=None, id_periodo=None, usuario_actual=None) -> list[Curso]:
        # RN-10a: un Estudiante solo ve los cursos de su grado y año de matrícula.
        # Se ignora el id_grado recibido, igual que listar_matriculas ignora el
        # id_estudiante recibido (RN-04): el alcance no se negocia con el cliente.
        if usuario_actual is not None and usuario_actual.rol == "Estudiante":
            return self.curso_repo.listar_para_estudiante(
                usuario_actual.id_usuario, id_periodo=id_periodo
            )

        return self.curso_repo.listar(id_docente=id_docente, id_grado=id_grado, id_periodo=id_periodo)

    def obtener_curso(self, id_curso: int, usuario_actual=None) -> Curso:
        curso = self.curso_repo.buscar_por_id(id_curso)
        if not curso:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

        # RN-10c: sin esto un Estudiante podía recorrer ids y leer el docente de
        # cualquier curso, esquivando el alcance que aplica listar_cursos. Se
        # responde 404 (no 403) para no confirmar que el curso existe.
        if usuario_actual is not None and usuario_actual.rol == "Estudiante":
            suyos = self.curso_repo.listar_para_estudiante(usuario_actual.id_usuario)
            if id_curso not in {c.id_curso for c in suyos}:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

        return curso

    def crear_matricula(self, id_estudiante: int, id_grado: int, anio: int, usuario_actual=None) -> Matricula:
        if usuario_actual is not None and usuario_actual.rol != "Administrador":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo los administradores pueden crear matrículas")

        estudiante = self.session.get(Estudiante, id_estudiante)
        if not estudiante:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")

        grado = self.grado_repo.buscar_por_id(id_grado)
        if not grado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grado no encontrado")

        usuario_estudiante = self.session.get(Usuario, id_estudiante)
        if usuario_estudiante is None or getattr(usuario_estudiante, "rol", None) != "Estudiante":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El estudiante debe existir y tener rol Estudiante")

        matriculas_existentes = self.matricula_repo.buscar_por_estudiante_y_anio(id_estudiante, anio)
        if matriculas_existentes:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El estudiante ya tiene una matrícula activa en este año")

        matricula = Matricula(id_estudiante=id_estudiante, id_grado=id_grado, anio=anio)
        return self.matricula_repo.crear(matricula)

    def listar_matriculas(self, id_grado=None, anio=None, id_estudiante=None, usuario_actual=None) -> list[Matricula]:
        # RN-04: un Estudiante solo puede consultar sus propias matrículas
        if usuario_actual is not None and usuario_actual.rol == "Estudiante":
            id_estudiante = usuario_actual.id_usuario
        return self.matricula_repo.listar(id_grado=id_grado, anio=anio, id_estudiante=id_estudiante)

    def listar_estudiantes_por_grado(self, id_grado: int, anio: int | None = None, usuario_actual=None) -> list[dict]:
        grado = self.grado_repo.buscar_por_id(id_grado)
        if not grado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grado no encontrado")

        # RN-03: el listado incluye nombres y correos, así que un Docente solo puede
        # pedirlo para los grados a los que le dicta algún curso. Sin esto bastaba con
        # recorrer id_grado para extraer el directorio completo del colegio. Se responde
        # 404 (no 403), igual que obtener_curso, para no confirmar que el grado existe.
        if usuario_actual is not None and usuario_actual.rol == "Docente":
            cursos_del_docente = self.curso_repo.listar(id_docente=usuario_actual.id_usuario, id_grado=id_grado)
            if not cursos_del_docente:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grado no encontrado")

        query = (
            select(
                Matricula.id_estudiante,
                Usuario.nombres,
                Usuario.apellidos,
                Usuario.correo,
                Usuario.documento,
            )
            .join(Estudiante, Estudiante.id_estudiante == Matricula.id_estudiante)
            .join(Usuario, Usuario.id_usuario == Estudiante.id_estudiante)
            .where(Matricula.id_grado == id_grado)
        )

        if anio is not None:
            query = query.where(Matricula.anio == anio)

        rows = self.session.execute(query).all()
        return [
            {
                "id_estudiante": row.id_estudiante,
                "nombre": row.nombres,
                "apellido": row.apellidos,
                "correo": row.correo,
                # HU22: llega null para los usuarios creados antes de la columna.
                # Lo consume el buscador de HU12 ("Nombre o documento").
                "documento": row.documento,
            }
            for row in rows
        ]

    def listar_cursos_docente(self, id_docente: int | None = None, usuario_actual=None):
        if usuario_actual is not None and usuario_actual.rol != "Docente":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para consultar estos cursos")

        if id_docente is None:
            if usuario_actual is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Se requiere el docente autenticado")
            id_docente = usuario_actual.id_usuario
        elif usuario_actual is not None and id_docente != usuario_actual.id_usuario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes consultar cursos de otro docente")

        cursos = self.curso_repo.listar_por_docente(id_docente)

        return [
            self._serializar_curso_docente(curso)
            for curso in cursos
        ]

    def listar_estudiantes_para_curso(self, id_curso: int, usuario_actual=None) -> dict:
        curso = self._obtener_curso_validado(id_curso, usuario_actual=usuario_actual)
        estudiantes = self._obtener_estudiantes_matriculados_del_curso(curso)

        asociados = [estudiante for estudiante in estudiantes if estudiante["asociado"]]
        disponibles = [estudiante for estudiante in estudiantes if not estudiante["asociado"]]

        return {
            "id_curso": curso.id_curso,
            "grado": curso.grado.nombre,
            "materia": curso.materia.nombre,
            "periodo": curso.periodo.nombre,
            "anio": self._obtener_anio_curso(curso),
            "estudiantes_disponibles": disponibles,
            "estudiantes_asociados": asociados,
        }

    def asociar_estudiante_a_curso(self, id_curso: int, id_estudiante: int, usuario_actual=None) -> dict:
        curso = self._obtener_curso_validado(id_curso, usuario_actual=usuario_actual)

        estudiante = self.session.get(Estudiante, id_estudiante)
        if not estudiante:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")

        anio_curso = self._obtener_anio_curso(curso)
        matricula = self.session.execute(
            select(Matricula).where(
                Matricula.id_estudiante == id_estudiante,
                Matricula.id_grado == curso.id_grado,
                Matricula.anio == anio_curso,
            )
        ).scalars().first()

        if not matricula:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El estudiante no tiene matrícula vigente para el grado del curso",
            )

        clave = (curso.id_curso, id_estudiante)
        if clave in self.asociaciones_curso_estudiante:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El estudiante ya fue agregado a este curso")

        self.asociaciones_curso_estudiante.add(clave)

        usuario_estudiante = self.session.get(Usuario, id_estudiante)
        return {
            "mensaje": "Estudiante agregado al curso correctamente",
            "curso": self._serializar_curso_docente(curso),
            "estudiante": {
                "id_estudiante": estudiante.id_estudiante,
                "nombres": usuario_estudiante.nombres if usuario_estudiante else "",
                "apellidos": usuario_estudiante.apellidos if usuario_estudiante else "",
                "correo": usuario_estudiante.correo if usuario_estudiante else None,
                "asociado": True,
            },
        }
            