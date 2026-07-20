from sqlalchemy import select
from app.models.actividad_evaluativa import ActividadEvaluativa


class ActividadEvaluativaRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, actividad: ActividadEvaluativa):
        self.session.add(actividad)
        self.session.commit()
        self.session.refresh(actividad)
        return actividad

    def listar(self, id_seccion=None):
        query = select(ActividadEvaluativa)

        if id_seccion is not None:
            query = query.where(ActividadEvaluativa.id_seccion == id_seccion)

        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_actividad):
        query = select(ActividadEvaluativa).where(ActividadEvaluativa.id_actividad == id_actividad)
        return self.session.execute(query).scalars().first()
