from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models.dia_asistible import DiaAsistible
from app.models.historial_asistencia import HistorialAsistencia

class AsistenciaRepository:
    
    def __init__(self, session : Session):
        self.session = session
        
    def consultar_dia_asistible(self, id_curso, fecha):
        query = select(DiaAsistible).where(
            DiaAsistible.id_curso == id_curso).where(DiaAsistible.fecha == fecha)
        return self.session.execute(query).scalars().first()
    
    def crear_dia_asistible(self, id_curso, fecha):
        dia_asistible = DiaAsistible(
            id_curso = id_curso, 
            fecha = fecha 
        ) 
        self.session.add(dia_asistible)
        
        self.session.flush()
        return dia_asistible
        
    def listar_historial(self, id_curso, fecha):
        dia_asistible = self.consultar_dia_asistible(id_curso, fecha)
        id_dia = dia_asistible.id_dia
        query = select(HistorialAsistencia).where(HistorialAsistencia.id_dia == id_dia)
        return self.session.execute(query).scalars().all()
    
    def listar_historial_estudiante(self, id_estudiante):
        query = select(HistorialAsistencia).where(HistorialAsistencia.id_estudiante == id_estudiante)
        return self.session.execute(query).scalars().all() 
        
    def obtener_historial(self, id_dia):
        query = (
            select(HistorialAsistencia)
            .where(HistorialAsistencia.id_dia == id_dia)
        )

        return self.session.execute(query).scalars().all()
    
    def actualizar_registro_asistencia(self,id_dia, id_estudiante, estado):
        query = update(HistorialAsistencia).where(
            HistorialAsistencia.id_dia == id_dia,
            HistorialAsistencia.id_estudiante == id_estudiante).values(estado = estado)
        
        resultado = self.session.execute(query)
        return resultado.rowcount