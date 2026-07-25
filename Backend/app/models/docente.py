from typing import TYPE_CHECKING
from app.core.database import Base 
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

#Evitar importaciones circulares
if TYPE_CHECKING: 
    from app.models.usuario import Usuario
    from app.models.curso import Curso
    
#Modelo de la tabla docente en la base de datos
class Docente(Base):
    __tablename__ = "docente"
    
    id_docente : Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), primary_key=True)
    
    estado : Mapped[str] = mapped_column(String(20))
    
    usuario : Mapped["Usuario"] = relationship(back_populates="rol_docente")
    cursos: Mapped[list["Curso"]] = relationship(back_populates="docente")

    # El nombre y el apellido del docente viven en Usuario, no aquí. La derivación
    # se hace en DocenteCursoResponse (app/schemas/curso.py) y no con @property:
    # una propiedad Python sobre una clase mapeada es invisible para el query layer
    # (Docente(nombre=...) revienta y where(Docente.nombre == ...) no filtra).

    def __repr__(self) -> str:
        return (
            f"Docente("
            f"id_docente={self.id_docente}, "
            f"estado='{self.estado}'"
            f")"
        )