from typing import TYPE_CHECKING, Optional
from app.core.database import Base
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

#Evitar importaciones circulares
if TYPE_CHECKING:
    from app.models.actividad_evaluativa import ActividadEvaluativa
    from app.models.estudiante import Estudiante

#Modelo de la tabla Nota en la base de datos
class Nota(Base):
    __tablename__ = "nota"

    id_nota: Mapped[int] = mapped_column(primary_key=True)

    id_actividad: Mapped[int] = mapped_column(ForeignKey("actividadevaluativa.id_actividad"))

    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiante.id_estudiante"))

    calificacion: Mapped[float] = mapped_column(Numeric(3, 2))

    comentario: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    actividad: Mapped["ActividadEvaluativa"] = relationship(back_populates="notas")
    estudiante: Mapped["Estudiante"] = relationship()

    def __repr__(self) -> str:
        return (
            f"Nota(id_nota={self.id_nota}, id_actividad={self.id_actividad}, "
            f"id_estudiante={self.id_estudiante}, calificacion={self.calificacion})"
        )
