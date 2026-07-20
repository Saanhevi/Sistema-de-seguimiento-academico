from sqlalchemy import select
from app.models.docente import Docente
from app.models.curso import Curso
from app.models.materia import Materia


class DocenteRepository:

    def __init__(self, session):
        self.session = session

    def crear_docente(self, docente: Docente):
        self.session.add(docente)
        self.session.commit()
        self.session.refresh(docente)
        return docente

    def obtener_materias(self, id_profesor):
        """Devuelve la lista de `Materia` asociadas a los cursos del docente.

        Se une la tabla `materia` con `curso` y se filtra por `id_docente`.
        Se usa `distinct` implícito al seleccionar materias para evitar duplicados
        cuando el docente dicta la misma materia en varios cursos/periodos.
        """
        query = select(Materia).join(Curso, Materia.id_materia == Curso.id_materia).where(
            Curso.id_docente == id_profesor
        )

        return self.session.execute(query).scalars().all()