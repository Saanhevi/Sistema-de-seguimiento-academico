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
    id_estudiante = Mapped[int] = mapped_column(ForeignKey("estudiante.id_dia"))
    estado = Mapped[str] = mapped_column(String(20))
    __table_args__ = (
        PrimaryKeyConstraint(
            "id_dia",
            "id_estudiante"
        ),
    )