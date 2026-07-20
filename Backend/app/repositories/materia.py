from app.models.materia import Materia
from sqlalchemy import select


class MateriaRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, materia: Materia):
        self.session.add(materia)
        self.session.commit()
        self.session.refresh(materia)
        return materia

    def listar(self):
        query = select(Materia)
        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_materia):
        query = select(Materia).where(Materia.id_materia == id_materia)
        return self.session.execute(query).scalars().first()
