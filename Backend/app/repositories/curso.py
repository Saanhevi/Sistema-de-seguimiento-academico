from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.curso import Curso
from app.models.docente import Docente
from app.models.matricula import Matricula
from app.models.periodo_academico import PeriodoAcademico


class CursoRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, curso: Curso):
        try:
            self.session.add(curso)
            self.session.commit()
            self.session.refresh(curso)
            # Se relee con los anidados cargados: CursoResponse serializa grado,
            # materia, periodo y docente, que si no dispararían 5 lazy loads.
            return self.buscar_por_id(curso.id_curso)
        except Exception:
            self.session.rollback()
            raise

    def _con_relaciones(self, query):
        # Carga grado/materia/periodo/docente en la misma query: evita el N+1 al
        # serializar los campos anidados de CursoResponse. Docente.usuario se
        # encadena porque el nombre/apellido del docente viven ahí, no en Docente.
        return query.options(
            joinedload(Curso.grado),
            joinedload(Curso.materia),
            joinedload(Curso.periodo),
            joinedload(Curso.docente).joinedload(Docente.usuario),
        )

    def listar(self, id_docente=None, id_grado=None, id_periodo=None):
        query = self._con_relaciones(select(Curso))

        if id_docente is not None:
            query = query.where(Curso.id_docente == id_docente)
        if id_grado is not None:
            query = query.where(Curso.id_grado == id_grado)
        if id_periodo is not None:
            query = query.where(Curso.id_periodo == id_periodo)

        return self.session.execute(query).scalars().all()

    def listar_para_estudiante(self, id_estudiante, id_periodo=None):
        """Cursos que el estudiante realmente cursa (RN-10a).

        Un curso cuenta como suyo si es del grado en el que está matriculado y el
        año del periodo del curso coincide con el año de esa matrícula. Sin la
        segunda condición el estudiante vería los cursos que ese mismo grado tuvo
        en cohortes de otros años.
        """
        query = (
            self._con_relaciones(select(Curso))
            .join(PeriodoAcademico, PeriodoAcademico.id_periodo == Curso.id_periodo)
            .join(
                Matricula,
                (Matricula.id_grado == Curso.id_grado)
                & (Matricula.anio == PeriodoAcademico.anio),
            )
            .where(Matricula.id_estudiante == id_estudiante)
        )

        if id_periodo is not None:
            query = query.where(Curso.id_periodo == id_periodo)

        return self.session.execute(query).scalars().unique().all()

    def buscar_por_id(self, id_curso):
        query = self._con_relaciones(select(Curso)).where(Curso.id_curso == id_curso)
        return self.session.execute(query).scalars().first()

    def buscar_por_combinacion(self, id_docente, id_grado, id_materia, id_periodo):
        query = select(Curso).where(
            Curso.id_docente == id_docente,
            Curso.id_grado == id_grado,
            Curso.id_materia == id_materia,
            Curso.id_periodo == id_periodo,
        )
        return self.session.execute(query).scalars().first()

    def listar_por_docente(self, id_docente: int):
        query = (
            select(Curso)
            .where(Curso.id_docente == id_docente)
        )

        return self.session.execute(query).scalars().all()