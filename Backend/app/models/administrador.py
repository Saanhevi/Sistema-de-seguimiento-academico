from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

#Evitar importaciones circulares
if TYPE_CHECKING: 
    from app.models.usuario import Usuario
    
#Modelo de la tabla admin en la base de datos
class Administrador(Base):
    __tablename__ = "administrador"
    
    id_admin : Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), primary_key=True)
    
    usuario : Mapped["Usuario"] = relationship(back_populates="rol_administrador")
    
    def __repr__(self) -> str:
        return f"Administrador(id_admin={self.id_admin})"