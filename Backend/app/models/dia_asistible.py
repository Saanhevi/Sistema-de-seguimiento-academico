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
    fecha: Mapped[date]

