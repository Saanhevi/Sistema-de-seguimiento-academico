"""
Pruebas de los cambios de curso.py que habilitan el módulo de calificaciones:

  - BE-2: CursoRepository carga grado/materia/periodo con joinedload y
    CursoResponse serializa esos anidados (el docente ve "Materia · Grado ·
    Periodo" y sabe si el periodo está Abierto sin llamadas extra).
  - BE-3: CursoService.listar_matriculas filtra por id_estudiante y, para el
    rol Estudiante, fuerza ese filtro a su propio id (RN-04).

Las pruebas del servicio usan dobles; la de serialización arma objetos ORM en
memoria sin tocar la base.
"""

import os
import unittest
from unittest.mock import Mock

from fastapi import HTTPException

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from app.models.curso import Curso
from app.models.docente import Docente
from app.models.grado import Grado
from app.models.materia import Materia
from app.models.periodo_academico import PeriodoAcademico
from app.models.usuario import Usuario
from app.schemas.curso import CursoResponse
from app.services.curso import CursoService


class ListarMatriculasTests(unittest.TestCase):
    """BE-3: filtro por estudiante y regla RN-04."""

    def setUp(self):
        self.service = CursoService(Mock())
        self.service.matricula_repo = Mock()
        self.service.matricula_repo.listar.return_value = []

    def test_estudiante_solo_ve_sus_propias_matriculas(self):
        # Aunque pida el id 500, el servicio lo ignora y usa el suyo (42).
        usuario = Usuario(id_usuario=42, rol="Estudiante")

        self.service.listar_matriculas(id_estudiante=500, usuario_actual=usuario)

        self.service.matricula_repo.listar.assert_called_once_with(
            id_grado=None, anio=None, id_estudiante=42
        )

    def test_admin_puede_filtrar_por_cualquier_estudiante(self):
        usuario = Usuario(id_usuario=1, rol="Administrador")

        self.service.listar_matriculas(id_estudiante=500, usuario_actual=usuario)

        self.service.matricula_repo.listar.assert_called_once_with(
            id_grado=None, anio=None, id_estudiante=500
        )

    def test_sin_usuario_respeta_el_filtro_recibido(self):
        self.service.listar_matriculas(id_grado=3, anio=2026, id_estudiante=7)

        self.service.matricula_repo.listar.assert_called_once_with(
            id_grado=3, anio=2026, id_estudiante=7
        )


class ListarEstudiantesPorGradoAlcanceTests(unittest.TestCase):
    """RN-03: el listado expone nombres y correos, así que el Docente solo puede
    pedirlo para los grados a los que dicta algún curso."""

    def setUp(self):
        self.service = CursoService(Mock())
        self.service.grado_repo = Mock()
        self.service.grado_repo.buscar_por_id.return_value = Grado(id_grado=3, nombre="10°")
        self.service.curso_repo = Mock()
        self.service.session = Mock()
        self.service.session.execute.return_value.all.return_value = []

    def test_docente_sin_curso_en_el_grado_recibe_404(self):
        self.service.curso_repo.listar.return_value = []
        usuario = Usuario(id_usuario=9, rol="Docente")

        with self.assertRaises(HTTPException) as contexto:
            self.service.listar_estudiantes_por_grado(id_grado=3, usuario_actual=usuario)

        # 404 y no 403: no se confirma que el grado exista.
        self.assertEqual(contexto.exception.status_code, 404)
        self.service.session.execute.assert_not_called()

    def test_docente_con_curso_en_el_grado_obtiene_el_listado(self):
        self.service.curso_repo.listar.return_value = [Curso(id_curso=1, id_docente=9, id_grado=3)]
        usuario = Usuario(id_usuario=9, rol="Docente")

        resultado = self.service.listar_estudiantes_por_grado(id_grado=3, usuario_actual=usuario)

        self.assertEqual(resultado, [])
        self.service.curso_repo.listar.assert_called_once_with(id_docente=9, id_grado=3)

    def test_administrador_no_tiene_restriccion_de_grado(self):
        usuario = Usuario(id_usuario=1, rol="Administrador")

        resultado = self.service.listar_estudiantes_por_grado(id_grado=3, usuario_actual=usuario)

        self.assertEqual(resultado, [])
        self.service.curso_repo.listar.assert_not_called()


class ListarCursosAlcanceTests(unittest.TestCase):
    """RN-10a (HU10): el Estudiante solo ve los cursos de su grado y año de matrícula."""

    def setUp(self):
        self.service = CursoService(Mock())
        self.service.curso_repo = Mock()
        self.service.curso_repo.listar.return_value = []
        self.service.curso_repo.listar_para_estudiante.return_value = []

    def test_estudiante_ignora_el_id_grado_recibido(self):
        # Pide el grado 99 (ajeno); el servicio lo descarta y consulta por su matrícula.
        usuario = Usuario(id_usuario=42, rol="Estudiante")

        self.service.listar_cursos(id_grado=99, usuario_actual=usuario)

        self.service.curso_repo.listar_para_estudiante.assert_called_once_with(42, id_periodo=None)
        self.service.curso_repo.listar.assert_not_called()

    def test_estudiante_conserva_el_filtro_de_periodo(self):
        usuario = Usuario(id_usuario=42, rol="Estudiante")

        self.service.listar_cursos(id_periodo=5, usuario_actual=usuario)

        self.service.curso_repo.listar_para_estudiante.assert_called_once_with(42, id_periodo=5)

    def test_docente_y_admin_conservan_sus_filtros(self):
        for rol in ("Docente", "Administrador"):
            with self.subTest(rol=rol):
                self.setUp()
                usuario = Usuario(id_usuario=1, rol=rol)

                self.service.listar_cursos(id_docente=3, id_grado=1, usuario_actual=usuario)

                self.service.curso_repo.listar.assert_called_once_with(
                    id_docente=3, id_grado=1, id_periodo=None
                )
                self.service.curso_repo.listar_para_estudiante.assert_not_called()

    def test_sin_usuario_no_aplica_alcance(self):
        self.service.listar_cursos(id_grado=7)

        self.service.curso_repo.listar.assert_called_once_with(
            id_docente=None, id_grado=7, id_periodo=None
        )

    def test_estudiante_no_puede_abrir_un_curso_ajeno_por_id(self):
        """RN-10c: recorrer /api/cursos/{id} no debe esquivar el alcance."""
        usuario = Usuario(id_usuario=42, rol="Estudiante")
        self.service.curso_repo.buscar_por_id.return_value = Curso(id_curso=99, id_docente=3)
        self.service.curso_repo.listar_para_estudiante.return_value = [Curso(id_curso=10)]

        with self.assertRaises(HTTPException) as ctx:
            self.service.obtener_curso(99, usuario_actual=usuario)

        self.assertEqual(ctx.exception.status_code, 404)

    def test_estudiante_si_puede_abrir_su_propio_curso(self):
        usuario = Usuario(id_usuario=42, rol="Estudiante")
        suyo = Curso(id_curso=10, id_docente=3)
        self.service.curso_repo.buscar_por_id.return_value = suyo
        self.service.curso_repo.listar_para_estudiante.return_value = [suyo]

        self.assertIs(self.service.obtener_curso(10, usuario_actual=usuario), suyo)

    def test_docente_abre_cualquier_curso_por_id(self):
        usuario = Usuario(id_usuario=1, rol="Docente")
        curso = Curso(id_curso=99, id_docente=3)
        self.service.curso_repo.buscar_por_id.return_value = curso

        self.assertIs(self.service.obtener_curso(99, usuario_actual=usuario), curso)
        self.service.curso_repo.listar_para_estudiante.assert_not_called()


class CursoResponseAnidadosTests(unittest.TestCase):
    """BE-2: los anidados grado/materia/periodo se serializan cuando existen."""

    def _curso_completo(self):
        curso = Curso(
            id_curso=10,
            id_docente=3,
            id_grado=1,
            id_materia=2,
            id_periodo=5,
        )
        curso.grado = Grado(id_grado=1, nombre="6A")
        curso.materia = Materia(id_materia=2, nombre="Matematicas")
        curso.periodo = PeriodoAcademico(id_periodo=5, nombre="Periodo 1", anio=2026, estado="Abierto")
        curso.docente = Docente(id_docente=3, estado="Activo")
        curso.docente.usuario = Usuario(id_usuario=3, nombres="Laura", apellidos="Gomez", rol="Docente")
        return curso

    def test_serializa_los_anidados(self):
        respuesta = CursoResponse.model_validate(self._curso_completo())

        self.assertEqual(respuesta.materia.nombre, "Matematicas")
        self.assertEqual(respuesta.grado.nombre, "6A")
        self.assertEqual(respuesta.periodo.estado, "Abierto")
        self.assertEqual(respuesta.periodo.anio, 2026)

    def test_serializa_el_docente(self):
        """HU10: el estudiante necesita ver el nombre del profesor del curso."""
        respuesta = CursoResponse.model_validate(self._curso_completo())

        self.assertEqual(respuesta.docente.id_docente, 3)
        self.assertEqual(respuesta.docente.nombre, "Laura")
        self.assertEqual(respuesta.docente.apellido, "Gomez")

    def test_docente_sin_usuario_no_rompe_la_respuesta(self):
        """RN-10d: una fila Docente huérfana degrada, no tumba la lista con un 500."""
        curso = Curso(id_curso=12, id_docente=3, id_grado=1, id_materia=2, id_periodo=5)
        curso.docente = Docente(id_docente=3, estado="Activo")  # sin .usuario

        respuesta = CursoResponse.model_validate(curso)

        self.assertEqual(respuesta.docente.id_docente, 3)
        self.assertIsNone(respuesta.docente.nombre)
        self.assertIsNone(respuesta.docente.apellido)

    def test_anidados_ausentes_quedan_en_none(self):
        curso = Curso(id_curso=11, id_docente=3, id_grado=1, id_materia=2, id_periodo=5)

        respuesta = CursoResponse.model_validate(curso)

        self.assertIsNone(respuesta.grado)
        self.assertIsNone(respuesta.materia)
        self.assertIsNone(respuesta.periodo)
        self.assertIsNone(respuesta.docente)
        # Los ids planos siguen presentes
        self.assertEqual(respuesta.id_grado, 1)


if __name__ == "__main__":
    unittest.main()
