from sqlalchemy import select, update, or_
from sqlalchemy.orm import joinedload
from app.models.alerta import Alerta
from app.models.curso import Curso
from app.models.estudiante import Estudiante
from app.models.periodo_academico import PeriodoAcademico


class AlertaRepository:

    def __init__(self, session):
        self.session = session

    def crear(self, alerta: Alerta) -> Alerta:
        try:
            self.session.add(alerta)
            self.session.commit()
            self.session.refresh(alerta)
            return alerta
        except Exception:
            self.session.rollback()
            raise

    def listar_por_estudiante(self, id_estudiante: int, estado: str | None = None) -> list[Alerta]:
        query = (
            select(Alerta)
            .options(
                joinedload(Alerta.estudiante).joinedload(Estudiante.usuario),
                joinedload(Alerta.curso).joinedload(Curso.periodo),
            )
            .outerjoin(Alerta.curso)
            .outerjoin(Curso.periodo)
            .where(Alerta.id_estudiante == id_estudiante)
        )
        if estado is not None:
            query = query.where(Alerta.estado == estado)
        query = query.where(
            or_(Alerta.id_curso.is_(None), PeriodoAcademico.estado == "Abierto")
        )
        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_alerta: int) -> Alerta | None:
        query = select(Alerta).where(Alerta.id_alerta == id_alerta)
        return self.session.execute(query).scalars().first()

    def buscar_por_tipo_curso(self, id_estudiante: int, tipo: str, id_curso: int | None):
        query = select(Alerta).where(
            Alerta.id_estudiante == id_estudiante,
            Alerta.tipo == tipo,
            Alerta.id_curso == id_curso,
            Alerta.estado.in_(('Pendiente', 'Vista')),
        )
        if id_curso is not None:
            query = query.join(Alerta.curso).join(Curso.periodo).where(PeriodoAcademico.estado == "Abierto")
        return self.session.execute(query).scalars().first()

    def listar_por_docente(self, id_docente: int, estado: str | None = None) -> list[Alerta]:
        query = (
            select(Alerta)
            .options(
                joinedload(Alerta.estudiante).joinedload(Estudiante.usuario),
                joinedload(Alerta.curso).joinedload(Curso.periodo),
            )
            .join(Alerta.curso)
            .join(Curso.periodo)
            .where(
                Curso.id_docente == id_docente,
                PeriodoAcademico.estado == "Abierto",
            )
        )
        if estado is not None:
            query = query.where(Alerta.estado == estado)
        return self.session.execute(query).scalars().all()

    def actualizar_estado(self, id_alerta: int, nuevo_estado: str) -> None:
        try:
            stmt = update(Alerta).where(Alerta.id_alerta == id_alerta).values(estado=nuevo_estado)
            self.session.execute(stmt)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
    def borrar_por_id(self, id_alerta: int) -> None:
        try:
            stmt = Alerta.__table__.delete().where(Alerta.id_alerta == id_alerta)
            self.session.execute(stmt)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
    def buscar_similar(self, id_estudiante: int, tipo: str, nivel: str, id_curso: int | None):
        # Busca una alerta pendiente o vista del mismo tipo/nivel/curso para el estudiante
        query = select(Alerta).where(
            Alerta.id_estudiante == id_estudiante,
            Alerta.tipo == tipo,
            Alerta.id_curso == id_curso,
            Alerta.nivel == nivel,
            Alerta.estado.in_(('Pendiente', 'Vista')),
        )
        if id_curso is not None:
            query = query.join(Alerta.curso).join(Curso.periodo).where(PeriodoAcademico.estado == 'Abierto')
        return self.session.execute(query).scalars().first()

    def actualizar_campos(self, id_alerta: int, **campos) -> None:
        try:
            stmt = update(Alerta).where(Alerta.id_alerta == id_alerta).values(**campos)
            self.session.execute(stmt)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
