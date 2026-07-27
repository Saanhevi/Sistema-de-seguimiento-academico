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


class ActualizarNotaTests(unittest.TestCase):
    """PUT /api/notas debe actualizar solo notas existentes."""

    def setUp(self):
        self.session = Mock()
        self.service = CalificacionService(self.session)
        self.service.actividad_repo = Mock()
        self.service.nota_repo = Mock()
        self.service.actividad_repo.buscar_por_id.return_value = _actividad()
        self.service._validar_pertenencia_curso = Mock()
        self.service._validar_calificacion = Mock()
        self.service._validar_estudiante = Mock()
        self.service._validar_periodo_abierto = Mock()
        self.service._bloquear_nota = Mock()

    def test_actualizar_nota_rechaza_si_no_existe(self):
        self.service.nota_repo.buscar_por_actividad_y_estudiante.return_value = None

        with self.assertRaises(HTTPException) as exc:
            self.service.actualizar_nota(10, 42, 4.0, "Sin nota", Usuario(id_usuario=3, rol="Docente"))

        self.assertEqual(exc.exception.status_code, 404)

    def test_actualizar_nota_modifica_nota_existente(self):
        nota = Mock(calificacion=3.0, comentario="vieja")
        self.service.nota_repo.buscar_por_actividad_y_estudiante.return_value = nota

        resultado = self.service.actualizar_nota(10, 42, 4.5, "mejor", Usuario(id_usuario=3, rol="Docente"))

        self.assertEqual(resultado.calificacion, 4.5)
        self.assertEqual(resultado.comentario, "mejor")
        self.service._bloquear_nota.assert_called_once_with(10, 42)
        self.session.flush.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(nota)

    def test_cargar_notas_masivo_preserva_comentario_existente(self):
        nota = Mock(calificacion=3.0, comentario="Buen trabajo")
        self.service.nota_repo.buscar_por_actividad_y_estudiante.return_value = nota
        self.service.nota_repo.agregar = Mock()

        resultado = self.service.cargar_notas_masivo(
            10,
            [{"id_estudiante": 42, "calificacion": 4.0}],
            Usuario(id_usuario=3, rol="Docente"),
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].comentario, "Buen trabajo")
        self.service.nota_repo.buscar_por_actividad_y_estudiante.assert_called_once_with(10, 42)
        self.session.commit.assert_called_once()

    def test_bloquear_nota_adquiere_lock_de_actividad_y_nota(self):
        session = Mock()
        service = CalificacionService(session)

        service._bloquear_nota(10, 42)

        self.assertEqual(session.execute.call_count, 2)
        self.assertEqual(session.execute.call_args_list[0][0][1], {"id_actividad": 10})
        self.assertEqual(session.execute.call_args_list[1][0][1], {"id_actividad": 10, "id_estudiante": 42})


class EliminacionTransaccionalTests(unittest.TestCase):
    """HU16: las eliminaciones deben revertir la transacción ante fallos."""

    def test_eliminar_actividad_hace_rollback_si_falla(self):
        session = Mock()
        service = CalificacionService(session)
        service.actividad_repo = Mock()
        service.nota_repo = Mock()
        service.actividad_repo.buscar_por_id.return_value = Mock(id_actividad=7, seccion=Mock(curso=_curso()))
        session.execute.return_value = Mock(scalars=Mock(all=Mock(return_value=[])))
        service.nota_repo.borrar_por_actividad.side_effect = RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            service.eliminar_actividad(7, Usuario(id_usuario=3, rol="Docente"))

        session.rollback.assert_called_once()

    def test_eliminar_seccion_llama_borrar_por_actividades(self):
        session = Mock()
        service = CalificacionService(session)
        service.seccion_repo = Mock()
        service.actividad_repo = Mock()
        service.nota_repo = Mock()
        seccion = Mock(id_seccion=11, curso=_curso())
        seccion.curso.periodo = Mock(estado="Abierto")
        service.seccion_repo.buscar_por_id.return_value = seccion
        service.actividad_repo.listar.return_value = [Mock(id_actividad=21), Mock(id_actividad=22)]
        session.execute.return_value = Mock(scalars=Mock(all=Mock(return_value=[])))

        service.eliminar_seccion(11, Usuario(id_usuario=3, rol="Docente"))

        service.nota_repo.borrar_por_actividades.assert_called_once_with([21, 22])
        service.nota_repo.borrar_por_actividad.assert_not_called()

    def test_eliminar_seccion_hace_rollback_si_falla(self):
        session = Mock()
        service = CalificacionService(session)
        service.seccion_repo = Mock()
        service.actividad_repo = Mock()
        service.nota_repo = Mock()
        seccion = Mock(id_seccion=11, curso=_curso())
        seccion.curso.periodo = Mock(estado="Abierto")
        service.seccion_repo.buscar_por_id.return_value = seccion
        service.actividad_repo.listar.return_value = [Mock(id_actividad=21)]
        session.execute.return_value = Mock(scalars=Mock(all=Mock(return_value=[])))
        service.nota_repo.borrar_por_actividades.side_effect = RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            service.eliminar_seccion(11, Usuario(id_usuario=3, rol="Docente"))

        session.rollback.assert_called_once()


class ListarNotasRolTests(unittest.TestCase):
    """RN-04 y RN-03 en la ruta de lectura."""

    def setUp(self):
        self.service = CalificacionService(Mock())
        self.service.nota_repo = Mock()
        self.service.nota_repo.listar.return_value = []

    def test_estudiante_solo_ve_sus_notas(self):
        estudiante = Usuario(id_usuario=42, rol="Estudiante")
        self.service.listar_notas(id_actividad=8, usuario=estudiante)
        self.service.nota_repo.listar.assert_called_once_with(
            id_actividad=8, id_estudiante=42, id_docente=None
        )

    def test_docente_ve_todas_las_notas_de_la_actividad(self):
        docente = Usuario(id_usuario=3, rol="Docente")
        self.service.listar_notas(id_actividad=8, usuario=docente)
        # No se acota por estudiante (ve a todo el curso), pero sí por docente.
        self.service.nota_repo.listar.assert_called_once_with(
            id_actividad=8, id_estudiante=None, id_docente=3
        )

    def test_docente_sin_actividad_sigue_acotado_a_sus_cursos(self):
        # RN-03: sin este filtro, GET /api/notas sin id_actividad degeneraba en un
        # select(Nota) sin cláusulas y devolvía todas las notas de la institución.
        docente = Usuario(id_usuario=3, rol="Docente")
        self.service.listar_notas(id_actividad=None, usuario=docente)
        self.service.nota_repo.listar.assert_called_once_with(
            id_actividad=None, id_estudiante=None, id_docente=3
        )

    def test_administrador_no_tiene_restriccion(self):
        admin = Usuario(id_usuario=1, rol="Administrador")
        self.service.listar_notas(id_actividad=None, usuario=admin)
        self.service.nota_repo.listar.assert_called_once_with(
            id_actividad=None, id_estudiante=None, id_docente=None
        )


if __name__ == "__main__":
    unittest.main()
