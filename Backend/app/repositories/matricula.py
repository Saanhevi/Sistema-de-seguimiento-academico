from sqlalchemy import select
from app.models.matricula import Matricula


class MatriculaRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, matricula: Matricula):
        self.session.add(matricula)
        self.session.commit()
        self.session.refresh(matricula)
        return matricula

    def listar(self, id_grado=None, anio=None):
        query = select(Matricula)

        if id_grado is not None:
            query = query.where(Matricula.id_grado == id_grado)
        if anio is not None:
            query = query.where(Matricula.anio == anio)

        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_matricula):
        query = select(Matricula).where(Matricula.id_matricula == id_matricula)
        return self.session.execute(query).scalars().first()

    def buscar_por_estudiante_y_anio(self, id_estudiante, anio):
        query = select(Matricula).where(
            Matricula.id_estudiante == id_estudiante,
            Matricula.anio == anio,
        )
        return self.session.execute(query).scalars().all()
