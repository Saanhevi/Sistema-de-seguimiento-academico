from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.docente import Docente
    from app.models.grado import Grado
    from app.models.materia import Materia
    from app.models.periodo_academico import PeriodoAcademico
    from app.models.dia_asistible import DiaAsistible

class Curso(Base):
    __tablename__ = "curso"

    id_curso: Mapped[int] = mapped_column(primary_key=True)
    id_docente: Mapped[int] = mapped_column(ForeignKey("docente.id_docente"))
    id_grado: Mapped[int] = mapped_column(ForeignKey("grado.id_grado"))
    id_materia: Mapped[int] = mapped_column(ForeignKey("materia.id_materia"))
    id_periodo: Mapped[int] = mapped_column(ForeignKey("periodoacademico.id_periodo"))

    docente: Mapped["Docente"] = relationship(back_populates="cursos")
    grado: Mapped["Grado"] = relationship(back_populates="cursos")
    materia: Mapped["Materia"] = relationship(back_populates="cursos")
    periodo: Mapped["PeriodoAcademico"] = relationship(back_populates="cursos")
    dias_asistibles : Mapped[list["DiaAsistible"]] = relationship(back_populates="curso")
    
    def __repr__(self) -> str:
        return (
            f"Curso(id_curso={self.id_curso}, id_docente={self.id_docente}, "
            f"id_grado={self.id_grado}, id_materia={self.id_materia}, "
            f"id_periodo={self.id_periodo})"
        )
