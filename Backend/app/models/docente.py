from typing import TYPE_CHECKING
from app.core.database import Base 
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

#Evitar importaciones circulares
if TYPE_CHECKING: 
    from app.models.usuario import Usuario
    
#Modelo de la tabla docente en la base de datos
class Docente(Base):
    __tablename__ = "docente"
    
    id_docente : Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), primary_key=True)
    
    estado : Mapped[str] = mapped_column(String(20))
    
    usuario : Mapped["Usuario"] = relationship(back_populates="rol_docente")
    
    def __repr__(self) -> str:
        return (
            f"Docente("
            f"id_docente={self.id_docente}, "
            f"estado='{self.estado}'"
            f")"
        )