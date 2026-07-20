import unittest
from unittest.mock import Mock

from fastapi import HTTPException

from app.models.docente import Docente
from app.models.usuario import Usuario
from app.services.curso import CursoService


class CursoServiceRegressionTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock()
        self.service = CursoService(self.session)

    def test_docente_no_puede_crear_curso_para_otro_docente(self):
        self.session.get.side_effect = lambda model, pk: Docente(id_docente=1, estado="Activo") if model is Docente else None
        self.service.grado_repo.buscar_por_id = Mock(return_value=Mock(id_grado=1))
        self.service.materia_repo.buscar_por_id = Mock(return_value=Mock(id_materia=1))
        self.service.periodo_repo.buscar_por_id = Mock(return_value=Mock(id_periodo=1))
        self.service.curso_repo.buscar_por_combinacion = Mock(return_value=None)

        usuario_actual = Usuario(id_usuario=99, rol="Docente")

        with self.assertRaises(HTTPException) as exc:
            self.service.crear_curso(2, 1, 1, 1, usuario_actual=usuario_actual)

        self.assertEqual(exc.exception.status_code, 403)

    def test_crear_periodo_rechaza_anio_negativo(self):
        with self.assertRaises(HTTPException) as exc:
            self.service.crear_periodo("Periodo 1", -1, "Abierto")

        self.assertEqual(exc.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
