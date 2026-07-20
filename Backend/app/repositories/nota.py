from sqlalchemy import select
from app.models.nota import Nota


class NotaRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, nota: Nota):
        self.session.add(nota)
        self.session.commit()
        self.session.refresh(nota)
        return nota

    def actualizar(self, nota: Nota):
        self.session.commit()
        self.session.refresh(nota)
        return nota

    def listar(self, id_actividad=None):
        query = select(Nota)

        if id_actividad is not None:
            query = query.where(Nota.id_actividad == id_actividad)

        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_nota):
        query = select(Nota).where(Nota.id_nota == id_nota)
        return self.session.execute(query).scalars().first()

    def buscar_por_actividad_y_estudiante(self, id_actividad, id_estudiante):
        query = select(Nota).where(
            Nota.id_actividad == id_actividad,
            Nota.id_estudiante == id_estudiante,
        )
        return self.session.execute(query).scalars().first()
