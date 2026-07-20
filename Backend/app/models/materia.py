from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.curso import Curso


class Materia(Base):
    __tablename__ = "materia"

    id_materia: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))

    cursos: Mapped[list["Curso"]] = relationship(back_populates="materia")

    def __repr__(self) -> str:
        return f"Materia(id_materia={self.id_materia}, nombre='{self.nombre}')"
