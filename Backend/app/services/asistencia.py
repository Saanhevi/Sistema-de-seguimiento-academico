from datetime import date
from typing import Any
from sqlalchemy.orm import Session

# TODO: Reemplazar este stub por un servicio real con repositorios, validaciones y reglas de negocio.
class AsistenciaService:
    """Servicio temporal para el módulo de asistencia.

    Este módulo se deja preparado para crecer hacia integración con base de datos,
    pero en esta iteración ofrece un comportamiento mínimo para que la API pueda
    importarse correctamente.
    """
    def __init__(self, session : Session):
        self.session = session
    
    
    # TODO: Implementar la creación real de días asistibles con validación de curso y fechas.
    def crear_dia_asistible(self, id_curso: int, request: Any) -> dict[str, Any]:
        return {
            "id_dia": 0,
            "fecha": request.fecha,
            "id_curso": id_curso,
        }

    # TODO: Consultar la asistencia registrada para un día concreto desde la base de datos.
    def obtener_asistencia(self, id_dia: int) -> list[dict[str, Any]]:
        return []

    # TODO: Implementar el registro real de asistencia y manejar conflictos/duplicados.
    def registrar_asistencia(self, id_dia: int, requests: list[Any]) -> dict[str, str]:
        return {
            "mensaje": f"Asistencia registrada para el día {id_dia} (módulo en desarrollo)",
        }

    # TODO: Traer el historial real del estudiante desde la tabla de asistencia.
    def obtener_historial_asistencia(self, id_estudiante: int) -> list[dict[str, Any]]:
        return []
