from sqlalchemy import delete, select, func
from app.models.nota import Nota
from app.models.actividad_evaluativa import ActividadEvaluativa
from app.models.seccion_porcentaje import SeccionPorcentaje
from app.models.curso import Curso


class NotaRepository:

    def __init__(self, session):
        self.session = session

    def agregar(self, nota: Nota):
        # No hace commit: el llamador controla el límite de la transacción
        # (necesario para que carga-masiva confirme todo el lote en un solo commit)
        self.session.add(nota)
        self.session.flush()
        return nota

    def listar(self, id_actividad=None, id_estudiante=None, id_docente=None):
        query = select(Nota)

        if id_actividad is not None:
            query = query.where(Nota.id_actividad == id_actividad)
        if id_estudiante is not None:
            query = query.where(Nota.id_estudiante == id_estudiante)
        if id_docente is not None:
            # RN-03: solo las notas de actividades que cuelgan de un curso del docente.
            query = (
                query.join(ActividadEvaluativa, ActividadEvaluativa.id_actividad == Nota.id_actividad)
                .join(SeccionPorcentaje, SeccionPorcentaje.id_seccion == ActividadEvaluativa.id_seccion)
                .join(Curso, Curso.id_curso == SeccionPorcentaje.id_curso)
                .where(Curso.id_docente == id_docente)
            )

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
    def obtener_promedio_estudiante_materia(self, id_estudiante: int, id_materia: int) -> float:
        from app.models.actividad_evaluativa import ActividadEvaluativa
        from app.models.seccion_porcentaje import SeccionPorcentaje
        from app.models.curso import Curso

        notas = (
            self.session.query(Nota)
            .join(ActividadEvaluativa, Nota.id_actividad == ActividadEvaluativa.id_actividad)
            .join(SeccionPorcentaje, ActividadEvaluativa.id_seccion == SeccionPorcentaje.id_seccion)
            .join(Curso, SeccionPorcentaje.id_curso == Curso.id_curso)
            .filter(
                Nota.id_estudiante == id_estudiante,
                Curso.id_materia == id_materia
            )
            .all()
        )

        if not notas:
            return 0.0

        calificaciones = [float(n.calificacion) for n in notas if n.calificacion is not None]
        return round(sum(calificaciones) / len(calificaciones), 2) if calificaciones else 0.0   
    def obtener_promedio_grupal_materia(self, id_materia: int, id_docente: int) -> float:
        from app.models.actividad_evaluativa import ActividadEvaluativa
        from app.models.seccion_porcentaje import SeccionPorcentaje
        from app.models.curso import Curso

        # Buscamos todas las notas de esa materia, pero SOLO de los cursos que dicta este profesor
        notas = (
            self.session.query(Nota)
            .join(ActividadEvaluativa, Nota.id_actividad == ActividadEvaluativa.id_actividad)
            .join(SeccionPorcentaje, ActividadEvaluativa.id_seccion == SeccionPorcentaje.id_seccion)
            .join(Curso, SeccionPorcentaje.id_curso == Curso.id_curso)
            .filter(
                Curso.id_materia == id_materia,
                Curso.id_docente == id_docente
            )
            .all()
        )

        if not notas:
            return 0.0

        calificaciones = [float(n.calificacion) for n in notas if n.calificacion is not None]
        return round(sum(calificaciones) / len(calificaciones), 2) if calificaciones else 0.0

    def borrar_por_actividad(self, id_actividad: int):
        # Borra todas las notas asociadas a una actividad con una sola sentencia.
        self.session.execute(
            delete(Nota).where(Nota.id_actividad == id_actividad)
        )
        self.session.flush()

    def borrar_por_actividades(self, id_actividades: list[int]):
        if not id_actividades:
            return
        self.session.execute(
            delete(Nota).where(Nota.id_actividad.in_(id_actividades))
        )
        self.session.flush()