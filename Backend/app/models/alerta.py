from typing import TYPE_CHECKING, Optional
from datetime import datetime
from app.core.database import Base
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Evitar importaciones circulares
if TYPE_CHECKING:
    from app.models.estudiante import Estudiante
    from app.models.curso import Curso


class Alerta(Base):
    __tablename__ = "alerta"

    id_alerta: Mapped[int] = mapped_column(primary_key=True)
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("estudiante.id_estudiante"))
    id_curso: Mapped[Optional[int]] = mapped_column(ForeignKey("curso.id_curso"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(100))
    mensaje: Mapped[str] = mapped_column(String(200))
    nivel: Mapped[str] = mapped_column(String(10))
    fecha: Mapped[datetime] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(20))

    estudiante: Mapped["Estudiante"] = relationship()
    curso: Mapped["Curso"] = relationship()

    @property
    def nombre_estudiante(self) -> str:
        if self.estudiante is None or self.estudiante.usuario is None:
            return ""
        return f"{self.estudiante.usuario.nombres} {self.estudiante.usuario.apellidos}"

    @property
    def nombre_curso(self) -> str | None:
        if self.curso is None:
            return None
        nombre_materia = getattr(self.curso.materia, 'nombre', None)
        nombre_grado = getattr(self.curso.grado, 'nombre', None)
        if nombre_materia and nombre_grado:
            return f"{nombre_materia} {nombre_grado}"
        if nombre_materia:
            return nombre_materia
        if nombre_grado:
            return nombre_grado
        return None

    def __repr__(self) -> str:
        return (
            f"Alerta(id_alerta={self.id_alerta}, id_estudiante={self.id_estudiante}, "
            f"tipo='{self.tipo}', nivel='{self.nivel}', estado='{self.estado}')"
        )
