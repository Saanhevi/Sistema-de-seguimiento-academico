from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING: 
    from app.models.estudiante import Estudiante
    from app.models.dia_asistible import DiaAsistible

class HistorialAsistencia(Base):
    __tablename__ = "historialasistencia"
    id_dia : Mapped[int] = mapped_column(ForeignKey("diaasistible.id_dia"))
    id_estudiante : Mapped[int] = mapped_column(ForeignKey("estudiante.id_estudiante"))
    estado : Mapped[str] = mapped_column(String(20))
    __table_args__ = (
        PrimaryKeyConstraint(
            "id_dia",
            "id_estudiante"
        ),
    )
    
    dia_asistible : Mapped["DiaAsistible"] = relationship(back_populates="historial_asistencias")
    estudiante : Mapped["Estudiante"] = relationship(back_populates="historial_asistencias")    
    
    def __repr__(self):
        return (
            f"HistorialAsistencia("
            f"id_dia={self.id_dia}, "
            f"id_estudiante={self.id_estudiante}, "
            f"estado='{self.estado}')"
        )