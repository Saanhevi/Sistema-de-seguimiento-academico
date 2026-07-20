from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

#Evitar importaciones circulares
if TYPE_CHECKING:
    from app.models.curso import Curso
    from app.models.actividad_evaluativa import ActividadEvaluativa

#Modelo de la tabla SeccionPorcentaje en la base de datos
class SeccionPorcentaje(Base):
    __tablename__ = "seccionporcentaje"

    id_seccion: Mapped[int] = mapped_column(primary_key=True)

    nombre_seccion: Mapped[str] = mapped_column(String(50))

    porcentaje: Mapped[float] = mapped_column(Numeric(5, 2))

    id_curso: Mapped[int] = mapped_column(ForeignKey("curso.id_curso"))

    curso: Mapped["Curso"] = relationship()
    actividades: Mapped[list["ActividadEvaluativa"]] = relationship(back_populates="seccion")

    def __repr__(self) -> str:
        return (
            f"SeccionPorcentaje(id_seccion={self.id_seccion}, nombre_seccion='{self.nombre_seccion}', "
            f"porcentaje={self.porcentaje}, id_curso={self.id_curso})"
        )
