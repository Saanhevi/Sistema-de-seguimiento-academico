from sqlalchemy import select
from app.models.nota import Nota


class NotaRepository:

    def __init__(self, session):
        self.session = session

    def agregar(self, nota: Nota):
        # No hace commit: el llamador controla el límite de la transacción
        # (necesario para que carga-masiva confirme todo el lote en un solo commit)
        self.session.add(nota)
        self.session.flush()
        return nota

    def listar(self, id_actividad=None, id_estudiante=None):
        query = select(Nota)

        if id_actividad is not None:
            query = query.where(Nota.id_actividad == id_actividad)
        if id_estudiante is not None:
            query = query.where(Nota.id_estudiante == id_estudiante)

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
