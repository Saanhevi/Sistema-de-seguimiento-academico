from sqlalchemy import delete, select
from app.models.actividad_evaluativa import ActividadEvaluativa
from app.models.seccion_porcentaje import SeccionPorcentaje


class ActividadEvaluativaRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, actividad: ActividadEvaluativa):
        self.session.add(actividad)
        self.session.commit()
        self.session.refresh(actividad)
        return actividad

    def listar(self, id_seccion=None, ids_curso=None):
        query = select(ActividadEvaluativa)

        if id_seccion is not None:
            query = query.where(ActividadEvaluativa.id_seccion == id_seccion)
        # ids_curso acota el listado a los cursos que el usuario puede leer.
        if ids_curso is not None:
            query = query.join(
                SeccionPorcentaje,
                SeccionPorcentaje.id_seccion == ActividadEvaluativa.id_seccion,
            ).where(SeccionPorcentaje.id_curso.in_(ids_curso))

        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_actividad):
        query = select(ActividadEvaluativa).where(ActividadEvaluativa.id_actividad == id_actividad)
        return self.session.execute(query).scalars().first()

    def borrar(self, actividad: ActividadEvaluativa):
        # El llamador debe encargarse del commit si requiere transacción mayor
        self.session.delete(actividad)
        self.session.flush()

    def borrar_por_seccion(self, id_seccion: int):
        self.session.execute(
            delete(ActividadEvaluativa).where(ActividadEvaluativa.id_seccion == id_seccion)
        )
        self.session.flush()
