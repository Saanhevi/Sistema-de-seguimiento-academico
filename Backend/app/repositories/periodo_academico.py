from app.models.periodo_academico import PeriodoAcademico
from sqlalchemy import select


class PeriodoAcademicoRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, periodo: PeriodoAcademico):
        self.session.add(periodo)
        self.session.commit()
        self.session.refresh(periodo)
        return periodo

    def listar(self):
        query = select(PeriodoAcademico)
        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_periodo):
        query = select(PeriodoAcademico).where(PeriodoAcademico.id_periodo == id_periodo)
        return self.session.execute(query).scalars().first()
