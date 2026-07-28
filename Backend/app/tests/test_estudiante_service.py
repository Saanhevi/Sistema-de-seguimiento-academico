import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from fastapi import HTTPException

from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.services.estudiante import EstudianteService


class EstudianteServiceRetiroTests(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.service = EstudianteService(self.session)

    def _mock_busqueda_por_id(self, estudiante):
        query = MagicMock()
        query.filter.return_value.first.return_value = estudiante
        self.session.query.return_value = query

    def test_retirar_estudiante_activo_lo_cambia_a_inactivo(self):
        estudiante = Estudiante(id_estudiante=7, estado="Activo")
        estudiante.usuario = Usuario(
            id_usuario=7,
            nombres="Ana",
            apellidos="Perez",
            correo="ana@colegio.edu.co",
            password_hash="hash",
            rol="Estudiante",
        )
        self._mock_busqueda_por_id(estudiante)

        respuesta = self.service.retirar(7)

        self.assertEqual(estudiante.estado, "Inactivo")
        self.session.commit.assert_called_once()
        self.assertEqual(respuesta["id"], 7)
        self.assertFalse(respuesta["estado"])

    def test_retirar_estudiante_ya_inactivo_es_idempotente(self):
        estudiante = Estudiante(id_estudiante=9, estado="Inactivo")
        estudiante.usuario = Usuario(
            id_usuario=9,
            nombres="Luis",
            apellidos="Rojas",
            correo="luis@colegio.edu.co",
            password_hash="hash",
            rol="Estudiante",
        )
        self._mock_busqueda_por_id(estudiante)

        respuesta = self.service.retirar(9)

        self.session.commit.assert_not_called()
        self.assertEqual(respuesta["id"], 9)
        self.assertFalse(respuesta["estado"])

    def test_retirar_estudiante_inexistente(self):
        self._mock_busqueda_por_id(None)

        with self.assertRaises(HTTPException) as exc:
            self.service.retirar(999)

        self.assertEqual(exc.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
