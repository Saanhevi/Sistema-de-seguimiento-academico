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

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from app.models.curso import Curso
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
        return curso

    def test_serializa_los_anidados(self):
        respuesta = CursoResponse.model_validate(self._curso_completo())

        self.assertEqual(respuesta.materia.nombre, "Matematicas")
        self.assertEqual(respuesta.grado.nombre, "6A")
        self.assertEqual(respuesta.periodo.estado, "Abierto")
        self.assertEqual(respuesta.periodo.anio, 2026)

    def test_anidados_ausentes_quedan_en_none(self):
        curso = Curso(id_curso=11, id_docente=3, id_grado=1, id_materia=2, id_periodo=5)

        respuesta = CursoResponse.model_validate(curso)

        self.assertIsNone(respuesta.grado)
        self.assertIsNone(respuesta.materia)
        self.assertIsNone(respuesta.periodo)
        # Los ids planos siguen presentes
        self.assertEqual(respuesta.id_grado, 1)


if __name__ == "__main__":
    unittest.main()
