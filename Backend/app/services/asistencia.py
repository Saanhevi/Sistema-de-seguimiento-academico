from datetime import date
from typing import Any
from sqlalchemy.orm import Session
from app.schemas.asistencia import AsistenciaRequest
# TODO: Reemplazar este stub por un servicio real con repositorios, validaciones y reglas de negocio.
class AsistenciaService:
    """Servicio temporal para el módulo de asistencia.

    Este módulo se deja preparado para crecer hacia integración con base de datos,
    pero en esta iteración ofrece un comportamiento mínimo para que la API pueda
    importarse correctamente.
    """
    def __init__(self, session : Session):
        self.session = session
    
    def lista_asistencia(self, id_curso, fecha):
        #Se verifica si hay un dia asistible para tal curso y fecha
        # Si no se hay se crea 
        # Si hay entonces se muestra directamente 
        if id_curso == 2 :
            return {
                    "id_dia": 2,
                    "grado": "string",
                    "materia": "string",
                    "fecha": "2026-07-23",
                    "asistencias": [
                        {
                        "id_estudiante": 0,
                        "nombres": "string",
                        "apellidos": "string",
                        "estado": "string"
                        }, 
                        {
                        "id_estudiante": 2,
                        "nombres": "string",
                        "apellidos": "string",
                        "estado": "string"
                        }
                    ]
                }
        else: 
            return {
                    "id_dia": 3,
                    "grado": "string",
                    "materia": "string",
                    "fecha": "2026-07-23",
                    "asistencias": [
                        {
                        "id_estudiante": 0,
                        "nombres": "string",
                        "apellidos": "string",
                        "estado": "string"
                        }, 
                        {
                        "id_estudiante": 2,
                        "nombres": "string",
                        "apellidos": "string",
                        "estado": "string"
                        }
                    ]
                } 
        
    def actualizar_asistencia(self, id_dia, lista_asistencia : list[AsistenciaRequest]):
        return {"mensaje" : "Actualizacion correcta"}
    
    def consultar_asistencias_estudiante(self, id_estudiante):
        return [
            {
                "materia": "Biologia",
                "fecha": "2026-07-22",
                "estado": "Ausente"
            }, 
            {
                "materia": "Matematicas",
                "fecha": "2026-07-22",
                "estado": "Presente"
            }
        ]
    
    def historial_dias_curso(self, id_curso):
        return [
            {
                "fecha": "2026-07-22"
            },            
            {
                "fecha": "2026-07-23"
            }
        ]
