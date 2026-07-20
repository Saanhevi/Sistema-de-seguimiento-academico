from sqlalchemy import select
from app.models.seccion_porcentaje import SeccionPorcentaje


class SeccionPorcentajeRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, seccion: SeccionPorcentaje):
        self.session.add(seccion)
        self.session.commit()
        self.session.refresh(seccion)
        return seccion

    def listar(self, id_curso=None):
        query = select(SeccionPorcentaje)

        if id_curso is not None:
            query = query.where(SeccionPorcentaje.id_curso == id_curso)

        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_seccion):
        query = select(SeccionPorcentaje).where(SeccionPorcentaje.id_seccion == id_seccion)
        return self.session.execute(query).scalars().first()
