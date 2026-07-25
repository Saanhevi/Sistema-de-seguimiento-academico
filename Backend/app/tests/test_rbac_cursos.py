"""RBAC del router de cursos, por HTTP y sin base de datos.

Estaba escrito como función suelta al estilo pytest, que no está en
requirements.txt: `unittest` no recoge funciones sueltas, así que el archivo
nunca llegaba a ejecutarse. Se pasa a unittest.TestCase, como el resto de la
suite, para que corra con el mismo runner:

    python -m unittest app.tests.test_rbac_cursos

Las peticiones se cortan en la capa de autenticación, antes de tocar la base,
así que no hace falta Docker.
"""

import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from fastapi.testclient import TestClient
from app.main import app


class RbacCursosTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_grados_requiere_autenticacion(self):
        respuesta = self.client.get("/api/grados")
        self.assertIn(respuesta.status_code, {401, 403})

    def test_endpoints_de_curso_requieren_autenticacion(self):
        for ruta in ("/api/cursos", "/api/cursos/1", "/api/materias",
                     "/api/periodos", "/api/matriculas", "/api/grados/1/estudiantes"):
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertIn(respuesta.status_code, {401, 403})

    def test_estudiante_por_id_ya_no_existe(self):
        """Se retiró GET /api/estudiantes/{id}: no tenía consumidor y filtraba correos.

        404 y no 401 confirma que la ruta desapareció, no que solo esté protegida.
        """
        respuesta = self.client.get("/api/estudiantes/1")
        self.assertEqual(respuesta.status_code, 404)
        self.assertNotIn("/api/estudiantes/{id_estudiante}", app.openapi()["paths"])


if __name__ == "__main__":
    unittest.main()
