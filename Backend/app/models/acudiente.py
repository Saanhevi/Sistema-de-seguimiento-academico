from typing import TYPE_CHECKING
from app.core.database import Base 
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

#Evitar importaciones circulares
if TYPE_CHECKING:
    from app.models.usuario import Usuario 
    
    
#Modelo de la tabla Acudiente en la base de datos
class Acudiente(Base):
    __tablename__ = "acudiente"
    
    id_acudiente : Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), primary_key=True) 
    
    usuario : Mapped["Usuario"] = relationship(back_populates="rol_acudiente")

    def __repr__(self) -> str:
        return f"Acudiente(id_acudiente={self.id_acudiente})"