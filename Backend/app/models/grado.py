from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.curso import Curso
    from app.models.matricula import Matricula


class Grado(Base):
    __tablename__ = "grado"

    id_grado: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(10))

    cursos: Mapped[list["Curso"]] = relationship(back_populates="grado")
    matriculas: Mapped[list["Matricula"]] = relationship(back_populates="grado")

    def __repr__(self) -> str:
        return f"Grado(id_grado={self.id_grado}, nombre='{self.nombre}')"
