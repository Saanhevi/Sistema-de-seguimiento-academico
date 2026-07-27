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

    def listar(self, id_curso=None, ids_curso=None):
        query = select(SeccionPorcentaje)

        if id_curso is not None:
            query = query.where(SeccionPorcentaje.id_curso == id_curso)
        # ids_curso acota el listado a los cursos que el usuario puede leer.
        # Una colección vacía es significativa (no ve ningún curso), así que se
        # compara contra None y no por veracidad.
        if ids_curso is not None:
            query = query.where(SeccionPorcentaje.id_curso.in_(ids_curso))

        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_seccion):
        query = select(SeccionPorcentaje).where(SeccionPorcentaje.id_seccion == id_seccion)
        return self.session.execute(query).scalars().first()

    def borrar(self, seccion: SeccionPorcentaje):
        # El llamador debe encargarse del commit si requiere transacción mayor
        self.session.delete(seccion)
        self.session.flush()
