from sqlalchemy.orm import Session
from app.schemas.asistencia import AsistenciaRequest
from app.repositories.asistencia import AsistenciaRepository
from app.repositories.curso import CursoRepository
from app.models.historial_asistencia import HistorialAsistencia

class AsistenciaService:
    """Servicio temporal para el módulo de asistencia.

    Este módulo se deja preparado para crecer hacia integración con base de datos,
    pero en esta iteración ofrece un comportamiento mínimo para que la API pueda
    importarse correctamente.
    """
    def __init__(self, session : Session):
        self.session = session
        self.asistencia_repository = AsistenciaRepository(session)
        self.curso_repository = CursoRepository(session)
        
    def lista_asistencia(self, id_curso, fecha):
        #Se verifica si hay un dia asistible para tal curso y fecha 
        # Si no existe, se crea automáticamente el día asistible
        # Si hay entonces se muestra directamente 
        
        dia_asistible = self.asistencia_repository.consultar_dia_asistible(id_curso, fecha)
        curso = self.curso_repository.buscar_por_id(id_curso)
        grado = curso.grado
        materia = curso.materia
        anio = curso.periodo.anio        
        # Las matriculas del mismo ano del curso
        matriculas = [
            m for m in grado.matriculas
            if m.anio == anio
        ]
        
        
        asistencias = []
        if not dia_asistible : 
            # No hay dia asistible
            dia_asistible_creado = self.asistencia_repository.crear_dia_asistible(id_curso, fecha)
            
            for matricula in matriculas:
                estudiante = matricula.estudiante
                id_estudiante = estudiante.id_estudiante
                nombres = estudiante.usuario.nombres 
                apellidos = estudiante.usuario.apellidos
                estado = "Presente"
                
                asistencia = {
                    "id_estudiante" : id_estudiante,
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "estado": estado
                }
                
                asistencias.append(asistencia)
                
                historial_asistencia = HistorialAsistencia(
                    id_dia = dia_asistible_creado.id_dia,
                    id_estudiante = id_estudiante,
                    estado = estado
                )
                
                self.session.add(historial_asistencia)
                            
            self.session.commit()   
            return {
                "id_dia": dia_asistible_creado.id_dia,
                "grado": grado.nombre,
                "materia": materia.nombre,
                "fecha": fecha,
                "asistencias": asistencias   
            }
            
        else:
            # Hay un dia asistible 
            id_dia = dia_asistible.id_dia
            historial = self.asistencia_repository.obtener_historial(id_dia)
            
            # Se hace un diccionario con la clave (id) y el estado
            estados = {
                h.id_estudiante : h.estado
                for h in historial
            }
            
            for matricula in matriculas:
                estudiante = matricula.estudiante
                id_estudiante = estudiante.id_estudiante
                nombres = estudiante.usuario.nombres 
                apellidos = estudiante.usuario.apellidos
                
                asistencia = {
                    "id_estudiante" :id_estudiante,
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "estado": estados[id_estudiante]
                }
                
                asistencias.append(asistencia)
                
            return {
                    "id_dia": id_dia,
                    "grado": grado.nombre,
                    "materia": materia.nombre,
                    "fecha": fecha,
                    "asistencias": asistencias
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
