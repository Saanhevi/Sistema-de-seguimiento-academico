from datetime import date
from typing import Any


class AsistenciaService:
    """Servicio temporal para el módulo de asistencia.

    Este módulo se deja preparado para crecer hacia integración con base de datos,
    pero en esta iteración ofrece un comportamiento mínimo para que la API pueda
    importarse correctamente.
    """

    def crear_dia_asistible(self, id_curso: int, request: Any) -> dict[str, Any]:
        return {
            "id_dia": 0,
            "fecha": request.fecha,
            "id_curso": id_curso,
        }

    def obtener_asistencia(self, id_dia: int) -> list[dict[str, Any]]:
        return []

    def registrar_asistencia(self, id_dia: int, requests: list[Any]) -> dict[str, str]:
        return {
            "mensaje": f"Asistencia registrada para el día {id_dia} (módulo en desarrollo)",
        }

    def obtener_historial_asistencia(self, id_estudiante: int) -> list[dict[str, Any]]:
        return []
