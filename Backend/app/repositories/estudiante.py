from app.models.estudiante import Estudiante
from sqlalchemy import select 

class EstudianteRepository: 
    
    def __init__(self, session):
        self.session = session 
        
    def crear_estudiante(self, estudiante : Estudiante):
        self.session.add(estudiante)
        self.session.commit()
        
        self.session.refresh(estudiante)
        return estudiante
    
    