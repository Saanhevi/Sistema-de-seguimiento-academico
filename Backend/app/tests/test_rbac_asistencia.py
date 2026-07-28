import os
import unittest
from datetime import date
from types import SimpleNamespace

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from fastapi.testclient import TestClient

from app.core.dependencies import get_asistencia_service, get_current_user
from app.main import app


class StubAsistenciaService:
    def __init__(self):
        self.calls = []

    # Las firmas deben seguir a AsistenciaService: los routers reenvian el usuario
    # autenticado para que el servicio valide que el curso es del docente.
    def lista_asistencia(self, id_curso, fecha, usuario=None):
        self.calls.append(("lista_asistencia", id_curso, fecha, usuario))
        return {
            "id_dia": 1,
            "grado": "10°",
            "materia": "Matemáticas",
            "fecha": fecha,
            "asistencias": [],
        }

    def actualizar_asistencia(self, id_dia, lista_asistencia, usuario=None):
        self.calls.append(("actualizar_asistencia", id_dia, lista_asistencia, usuario))
        return {"mensaje": "Actualizacion correcta"}

    def consultar_asistencias_estudiante(self, id_estudiante):
        self.calls.append(("consultar_asistencias_estudiante", id_estudiante))
        return []

    def historial_dias_curso(self, id_curso, usuario=None):
        self.calls.append(("historial_dias_curso", id_curso, usuario))
        return []


class UsuarioDocente:
    rol = "Docente"


class UsuarioEstudiante:
    rol = "Estudiante"
    rol_estudiante = SimpleNamespace(id_estudiante=7)


class RbacAsistenciaTests(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.service = StubAsistenciaService()
        app.dependency_overrides[get_asistencia_service] = lambda: self.service

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_lista_asistencias_requiere_autenticacion(self):
        respuesta = self.client.get("/api/asistencias/listas?id_curso=1&fecha=2026-07-23")

        self.assertIn(respuesta.status_code, {401, 403})
        self.assertEqual(self.service.calls, [])

    def test_guardar_asistencia_requiere_autenticacion(self):
        respuesta = self.client.put("/api/asistencias/listas/1", json=[])

        self.assertIn(respuesta.status_code, {401, 403})
        self.assertEqual(self.service.calls, [])

    def test_historial_dias_requiere_autenticacion(self):
        respuesta = self.client.get("/api/asistencias/listas/1")

        self.assertIn(respuesta.status_code, {401, 403})
        self.assertEqual(self.service.calls, [])

    def test_mis_asistencias_rechaza_docente(self):
        app.dependency_overrides[get_current_user] = lambda: UsuarioDocente()

        respuesta = self.client.get("/api/asistencias/mis-asistencias")

        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(respuesta.json()["detail"], "No tienes permiso para esta acción")
        self.assertEqual(self.service.calls, [])

    def test_mis_asistencias_usa_el_estudiante_autenticado(self):
        app.dependency_overrides[get_current_user] = lambda: UsuarioEstudiante()

        respuesta = self.client.get("/api/asistencias/mis-asistencias")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), [])
        self.assertEqual(self.service.calls, [("consultar_asistencias_estudiante", 7)])

    # Los tres casos de abajo si llegan al servicio, y fijan que el router le
    # reenvie el usuario autenticado. Sin ellos el stub nunca se ejecuta y sus
    # firmas pueden quedar desfasadas de AsistenciaService sin que nadie lo note.
    def test_lista_asistencias_reenvia_el_docente_al_servicio(self):
        docente = UsuarioDocente()
        app.dependency_overrides[get_current_user] = lambda: docente

        respuesta = self.client.get("/api/asistencias/listas?id_curso=1&fecha=2026-07-23")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            self.service.calls,
            [("lista_asistencia", 1, date(2026, 7, 23), docente)],
        )

    def test_guardar_asistencia_reenvia_el_docente_al_servicio(self):
        docente = UsuarioDocente()
        app.dependency_overrides[get_current_user] = lambda: docente

        respuesta = self.client.put("/api/asistencias/listas/1", json=[])

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(self.service.calls, [("actualizar_asistencia", 1, [], docente)])

    def test_historial_dias_reenvia_el_docente_al_servicio(self):
        docente = UsuarioDocente()
        app.dependency_overrides[get_current_user] = lambda: docente

        respuesta = self.client.get("/api/asistencias/listas/1")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(self.service.calls, [("historial_dias_curso", 1, docente)])


if __name__ == "__main__":
    unittest.main()
