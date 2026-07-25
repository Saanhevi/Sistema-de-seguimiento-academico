"""
Pruebas del CalificacionService: las reglas de negocio del módulo de notas.

  - RN-03: un Docente solo opera sobre sus propios cursos (403 en otro caso).
  - RN-a:  la calificación va de 0.00 a 5.00 (rechaza fuera de rango, NaN, Inf).
  - RN-b:  el porcentaje de una sección va entre 0 y 100; avisa si el curso
           supera 100% acumulado, sin bloquear.
  - RN-d:  no se registran notas si el periodo del curso no está 'Abierto'.
  - RN-04: un Estudiante solo puede listar sus propias notas.

Todo con dobles de prueba; no se toca la base de datos.
"""

import os
import unittest
from unittest.mock import Mock

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from fastapi import HTTPException

from app.models.usuario import Usuario
from app.services.calificacion import CalificacionService


def _curso(id_docente=3, estado_periodo="Abierto"):
    curso = Mock()
    curso.id_docente = id_docente
    curso.periodo = Mock(estado=estado_periodo)
    return curso


def _actividad(id_docente=3, estado_periodo="Abierto"):
    actividad = Mock()
    actividad.seccion = Mock()
    actividad.seccion.curso = _curso(id_docente, estado_periodo)
    return actividad


class PertenenciaCursoTests(unittest.TestCase):
    """RN-03."""

    def setUp(self):
        self.service = CalificacionService(Mock())

    def test_docente_ajeno_recibe_403(self):
        docente = Usuario(id_usuario=99, rol="Docente")
        with self.assertRaises(HTTPException) as exc:
            self.service._validar_pertenencia_curso(_curso(id_docente=3), docente)
        self.assertEqual(exc.exception.status_code, 403)

    def test_docente_dueno_pasa(self):
        docente = Usuario(id_usuario=3, rol="Docente")
        self.service._validar_pertenencia_curso(_curso(id_docente=3), docente)  # no lanza

    def test_administrador_pasa_sobre_cualquier_curso(self):
        admin = Usuario(id_usuario=1, rol="Administrador")
        self.service._validar_pertenencia_curso(_curso(id_docente=3), admin)  # no lanza


class CalificacionRangoTests(unittest.TestCase):
    """RN-a."""

    def setUp(self):
        self.service = CalificacionService(Mock())

    def test_acepta_los_extremos_validos(self):
        self.service._validar_calificacion(0)
        self.service._validar_calificacion(5)
        self.service._validar_calificacion(3.75)

    def test_rechaza_fuera_de_rango(self):
        for valor in (-0.01, 5.01, 10):
            with self.assertRaises(HTTPException) as exc:
                self.service._validar_calificacion(valor)
            self.assertEqual(exc.exception.status_code, 400)

    def test_rechaza_no_finitos_y_none(self):
        for valor in (float("nan"), float("inf"), None):
            with self.assertRaises(HTTPException) as exc:
                self.service._validar_calificacion(valor)
            self.assertEqual(exc.exception.status_code, 400)


class PeriodoAbiertoTests(unittest.TestCase):
    """RN-d."""

    def setUp(self):
        self.service = CalificacionService(Mock())

    def test_periodo_cerrado_bloquea(self):
        with self.assertRaises(HTTPException) as exc:
            self.service._validar_periodo_abierto(_actividad(estado_periodo="Cerrado"))
        self.assertEqual(exc.exception.status_code, 400)

    def test_periodo_abierto_pasa(self):
        self.service._validar_periodo_abierto(_actividad(estado_periodo="Abierto"))  # no lanza


class CrearSeccionTests(unittest.TestCase):
    """RN-b: rango del porcentaje y advertencia al superar 100%."""

    def setUp(self):
        self.service = CalificacionService(Mock())
        self.service.curso_repo = Mock()
        self.service.seccion_repo = Mock()
        self.docente = Usuario(id_usuario=3, rol="Docente")

    def test_porcentaje_fuera_de_rango_se_rechaza(self):
        self.service.curso_repo.buscar_por_id.return_value = _curso(id_docente=3)
        for valor in (0, -5, 150):
            with self.assertRaises(HTTPException) as exc:
                self.service.crear_seccion("Talleres", valor, id_curso=10, usuario=self.docente)
            self.assertEqual(exc.exception.status_code, 400)

    def test_curso_inexistente_da_404(self):
        self.service.curso_repo.buscar_por_id.return_value = None
        with self.assertRaises(HTTPException) as exc:
            self.service.crear_seccion("Talleres", 30, id_curso=999, usuario=self.docente)
        self.assertEqual(exc.exception.status_code, 404)

    def test_advierte_cuando_supera_100_sin_bloquear(self):
        self.service.curso_repo.buscar_por_id.return_value = _curso(id_docente=3)
        # Ya hay 80% registrado; agregar 30% lleva a 110%.
        self.service.seccion_repo.listar.return_value = [Mock(porcentaje=80)]
        creada = Mock(spec=["advertencia"])
        self.service.seccion_repo.crear.return_value = creada

        resultado = self.service.crear_seccion("Final", 30, id_curso=10, usuario=self.docente)

        self.assertIn("110", resultado.advertencia)

    def test_sin_exceso_no_pone_advertencia(self):
        self.service.curso_repo.buscar_por_id.return_value = _curso(id_docente=3)
        self.service.seccion_repo.listar.return_value = [Mock(porcentaje=40)]
        creada = SeccionFalsa()
        self.service.seccion_repo.crear.return_value = creada

        resultado = self.service.crear_seccion("Parcial", 30, id_curso=10, usuario=self.docente)

        self.assertFalse(hasattr(resultado, "advertencia"))


class SeccionFalsa:
    """Objeto mínimo para comprobar que NO se le agrega el atributo advertencia."""


class ListarNotasRolTests(unittest.TestCase):
    """RN-04."""

    def setUp(self):
        self.service = CalificacionService(Mock())
        self.service.nota_repo = Mock()
        self.service.nota_repo.listar.return_value = []

    def test_estudiante_solo_ve_sus_notas(self):
        estudiante = Usuario(id_usuario=42, rol="Estudiante")
        self.service.listar_notas(id_actividad=8, usuario=estudiante)
        self.service.nota_repo.listar.assert_called_once_with(id_actividad=8, id_estudiante=42)

    def test_docente_ve_todas_las_notas_de_la_actividad(self):
        docente = Usuario(id_usuario=3, rol="Docente")
        self.service.listar_notas(id_actividad=8, usuario=docente)
        self.service.nota_repo.listar.assert_called_once_with(id_actividad=8, id_estudiante=None)


if __name__ == "__main__":
    unittest.main()
