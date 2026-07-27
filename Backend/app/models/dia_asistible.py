from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

if TYPE_CHECKING:
    from app.models.historial_asistencia import HistorialAsistencia
    from app.models.curso import Curso

class DiaAsistible(Base):
    __tablename__ = "diaasistible"
    id_dia : Mapped[int] = mapped_column(primary_key=True)
    id_curso : Mapped[int] = mapped_column(ForeignKey("curso.id_curso"))
    fecha: Mapped[date] = mapped_column()
    
    historial_asistencias : Mapped[list["HistorialAsistencia"]] =relationship(back_populates="dia_asistible")
    curso : Mapped["Curso"] = relationship(back_populates="dias_asistibles")

    def __repr__(self):
        return (
            f"DiaAsistible("
            f"id_dia={self.id_dia}, "
            f"id_curso={self.id_curso}, "
            f"fecha={self.fecha})"
        )