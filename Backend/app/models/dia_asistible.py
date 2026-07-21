from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

if TYPE_CHECKING:
    from app.models.historial_asistencia import HistorialAsistencia
    from app.models.curso import Curso

# TODO: Completar este modelo con relaciones reales, constraints y nombres de columnas acordes al esquema.
class DiaAsistible(Base):
    __tablename__ = "diaasistible"
    id_dia : Mapped[int] = mapped_column(primary_key=True)
    id_curso : Mapped[int] = mapped_column(ForeignKey("curso.id_curso"))
    fecha: Mapped[date]

