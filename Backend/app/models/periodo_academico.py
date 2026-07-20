from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.curso import Curso


class PeriodoAcademico(Base):
    __tablename__ = "periodoacademico"

    id_periodo: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(20))
    anio: Mapped[int] = mapped_column()
    estado: Mapped[str] = mapped_column(String(20))

    cursos: Mapped[list["Curso"]] = relationship(back_populates="periodo")

    def __repr__(self) -> str:
        return (
            f"PeriodoAcademico(id_periodo={self.id_periodo}, nombre='{self.nombre}', "
            f"anio={self.anio}, estado='{self.estado}')"
        )
