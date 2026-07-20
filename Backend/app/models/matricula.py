from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.estudiante import Estudiante
    from app.models.grado import Grado


class Matricula(Base):
    __tablename__ = "matricula"

    id_matricula: Mapped[int] = mapped_column(primary_key=True)
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiante.id_estudiante"))
    id_grado: Mapped[int] = mapped_column(ForeignKey("grado.id_grado"))
    anio: Mapped[int] = mapped_column()

    estudiante: Mapped["Estudiante"] = relationship(back_populates="matriculas")
    grado: Mapped["Grado"] = relationship(back_populates="matriculas")

    def __repr__(self) -> str:
        return (
            f"Matricula(id_matricula={self.id_matricula}, id_estudiante={self.id_estudiante}, "
            f"id_grado={self.id_grado}, anio={self.anio})"
        )
