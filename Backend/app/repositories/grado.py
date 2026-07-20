from app.models.grado import Grado
from sqlalchemy import select


class GradoRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, grado: Grado):
        self.session.add(grado)
        self.session.commit()
        self.session.refresh(grado)
        return grado

    def listar(self):
        query = select(Grado)
        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_grado):
        query = select(Grado).where(Grado.id_grado == id_grado)
        return self.session.execute(query).scalars().first()
