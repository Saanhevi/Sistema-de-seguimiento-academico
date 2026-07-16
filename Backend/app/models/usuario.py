from typing import TYPE_CHECKING
from app.core.database import Base
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped , mapped_column, relationship

#Evitar importaciones circulares
if TYPE_CHECKING:
    from app.models.administrador import Administrador
    from app.models.docente import Docente
    from app.models.estudiante import Estudiante
    from app.models.acudiente import Acudiente

# Modelo de la tabla Usuario en la base de datos
class Usuario(Base):
    __tablename__ = "usuario"
    
    id_usuario : Mapped[int] = mapped_column(primary_key=True)
    
    nombres : Mapped[str] = mapped_column(String(100))
    
    apellidos : Mapped[str] = mapped_column(String(100))
    
    correo : Mapped[str] = mapped_column(String(100), unique=True)
    
    password_hash : Mapped[str] = mapped_column(Text)
    
    rol : Mapped[str] = mapped_column(String(20))

    rol_administrador : Mapped["Administrador"] = relationship(back_populates="usuario") 

    rol_docente : Mapped["Docente"] = relationship(back_populates="usuario")
    
    rol_estudiante : Mapped["Estudiante"] = relationship(back_populates="usuario")
    
    rol_acudiente : Mapped["Acudiente"] = relationship(back_populates="usuario")
    
    def __repr__(self) -> str:
        return (
            f"Usuario("
            f"id_usuario={self.id_usuario}, "
            f"correo='{self.correo}', "
            f"rol='{self.rol}'"
            f")"
        )
    
