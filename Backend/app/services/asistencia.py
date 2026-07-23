from sqlalchemy.orm import Session
from app.schemas.asistencia import AsistenciaRequest
from app.repositories.asistencia import AsistenciaRepository
from app.repositories.curso import CursoRepository
from app.models.historial_asistencia import HistorialAsistencia
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

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
        try:
            for registro in lista_asistencia:
                filas = self.asistencia_repository.actualizar_registro_asistencia(
                    id_dia,
                    registro.id_estudiante, 
                    registro.estado
                )

                if filas == 0:
                    raise HTTPException(
                        status_code=404,
                        detail=f"El estudiante {registro.id_estudiante} no pertenece a esta lista."
                    )
                
            self.session.commit()
            return {"mensaje" : "Actualizacion correcta"}
            
        except SQLAlchemyError:
            self.session.rollback()
            raise
    
    def consultar_asistencias_estudiante(self, id_estudiante):
        registros_asistencias = self.asistencia_repository.listar_historial_estudiante(id_estudiante)
        lista_asistencias = []
        
        for registro in registros_asistencias:
            dia = registro.dia_asistible
            lista_asistencias.append(
                {
                    "materia" : dia.curso.materia.nombre,
                    "fecha" : dia.fecha, 
                    "estado" : registro.estado
                }
            )
            
        return lista_asistencias
        
        """
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
        ]"""
    
    def historial_dias_curso(self, id_curso):
        curso = self.curso_repository.buscar_por_id(id_curso)
        dias_asistibles =  sorted(
            curso.dias_asistibles,
            key=lambda dia: dia.fecha,
            reverse=True
        )
        
        fechas = []

        for dia_asitible in dias_asistibles:
            fechas.append(
                {"fecha" : dia_asitible.fecha }
            )        
        return fechas
        """
        return [
            {
                "fecha": "2026-07-22"
            },            
            {
                "fecha": "2026-07-23"
            }
        ]"""
