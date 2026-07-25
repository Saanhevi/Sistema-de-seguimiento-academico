from types import SimpleNamespace

from app.routers.asistencia import consultar_mis_asistencias


class StubService:
    def __init__(self):
        self.calls = []

    def consultar_asistencias_estudiante(self, id_estudiante):
        self.calls.append(id_estudiante)
        return [
            {
                "materia": "Matemáticas",
                "fecha": "2026-07-23",
                "estado": "Ausente",
            }
        ]


class StubUsuario:
    rol = "Estudiante"
    rol_estudiante = SimpleNamespace(id_estudiante=7)


def test_consultar_mis_asistencias_usa_el_estudiante_autenticado():
    service = StubService()

    resultado = consultar_mis_asistencias(service=service, usuario=StubUsuario())

    assert resultado == [
        {
            "materia": "Matemáticas",
            "fecha": "2026-07-23",
            "estado": "Ausente",
        }
    ]
    assert service.calls == [7]
