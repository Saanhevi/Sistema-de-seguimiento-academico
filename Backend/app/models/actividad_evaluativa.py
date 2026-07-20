from datetime import date
from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

#Evitar importaciones circulares
if TYPE_CHECKING:
    from app.models.seccion_porcentaje import SeccionPorcentaje
    from app.models.nota import Nota

#Modelo de la tabla ActividadEvaluativa en la base de datos
class ActividadEvaluativa(Base):
    __tablename__ = "actividadevaluativa"

    id_actividad: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(String(50))

    fecha: Mapped[date] = mapped_column(Date)

    id_seccion: Mapped[int] = mapped_column(ForeignKey("seccionporcentaje.id_seccion"))

    seccion: Mapped["SeccionPorcentaje"] = relationship(back_populates="actividades")
    notas: Mapped[list["Nota"]] = relationship(back_populates="actividad")

    def __repr__(self) -> str:
        return (
            f"ActividadEvaluativa(id_actividad={self.id_actividad}, nombre='{self.nombre}', "
            f"fecha={self.fecha}, id_seccion={self.id_seccion})"
        )
