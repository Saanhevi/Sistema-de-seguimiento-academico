from sqlalchemy import select
from app.models.curso import Curso


class CursoRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, curso: Curso):
        self.session.add(curso)
        self.session.commit()
        self.session.refresh(curso)
        return curso

    def listar(self, id_docente=None, id_grado=None, id_periodo=None):
        query = select(Curso)

        if id_docente is not None:
            query = query.where(Curso.id_docente == id_docente)
        if id_grado is not None:
            query = query.where(Curso.id_grado == id_grado)
        if id_periodo is not None:
            query = query.where(Curso.id_periodo == id_periodo)

        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_curso):
        query = select(Curso).where(Curso.id_curso == id_curso)
        return self.session.execute(query).scalars().first()

    def buscar_por_combinacion(self, id_docente, id_grado, id_materia, id_periodo):
        query = select(Curso).where(
            Curso.id_docente == id_docente,
            Curso.id_grado == id_grado,
            Curso.id_materia == id_materia,
            Curso.id_periodo == id_periodo,
        )
        return self.session.execute(query).scalars().first()
