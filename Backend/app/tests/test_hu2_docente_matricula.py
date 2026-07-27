import os
import unittest
from unittest.mock import Mock

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from fastapi import HTTPException

from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.services.curso import CursoService


class Hu2DocenteMatriculaTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock()
        self.service = CursoService(self.session)

        self.estudiante = Estudiante(id_estudiante=10, estado="Activo")
        self.usuario_estudiante = Usuario(id_usuario=10, rol="Estudiante")

        self.session.get.side_effect = self._session_get
        self.service.grado_repo.buscar_por_id = Mock(return_value=Mock(id_grado=2))
        self.service.matricula_repo.buscar_por_estudiante_y_anio = Mock(return_value=[])
        self.service.matricula_repo.crear = Mock(return_value=Mock(id_matricula=88, id_estudiante=10, id_grado=2, anio=2026))

    def _session_get(self, model, pk):
        if model.__name__ == "Estudiante" and pk == 10:
            return self.estudiante
        if model.__name__ == "Usuario" and pk == 10:
            return self.usuario_estudiante
        return None

    def test_docente_puede_matricular_si_dicta_grado_en_anio(self):
        self.service._docente_puede_matricular_en_grado = Mock(return_value=True)

        docente = Usuario(id_usuario=5, rol="Docente")
        resultado = self.service.crear_matricula(10, 2, 2026, usuario_actual=docente)

        self.assertEqual(resultado.id_matricula, 88)
        self.service.matricula_repo.crear.assert_called_once()
        self.service._docente_puede_matricular_en_grado.assert_called_once_with(
            id_docente=5, id_grado=2, anio=2026
        )

    def test_docente_no_puede_matricular_fuera_de_su_grado_anio(self):
        self.service._docente_puede_matricular_en_grado = Mock(return_value=False)

        docente = Usuario(id_usuario=5, rol="Docente")

        with self.assertRaises(HTTPException) as exc:
            self.service.crear_matricula(10, 9, 2026, usuario_actual=docente)

        self.assertEqual(exc.exception.status_code, 403)
        self.service.matricula_repo.crear.assert_not_called()


if __name__ == "__main__":
    unittest.main()
