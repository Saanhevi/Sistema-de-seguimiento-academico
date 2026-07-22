from typing import TYPE_CHECKING
from app.core.database import Base 
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

#Evitar importaciones circulares
if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.matricula import Matricula
    from app.models.historial_asistencia import HistorialAsistencia
    
#Modelo de la tabla Estudiante en la base de datos 
class Estudiante(Base):
    __tablename__ = "estudiante"
    
    id_estudiante : Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), primary_key=True) 
    
    estado : Mapped[str] = mapped_column(String(20))   
    
    usuario : Mapped["Usuario"] = relationship(back_populates="rol_estudiante")
    matriculas: Mapped[list["Matricula"]] = relationship(back_populates="estudiante")
    
    historial_asistencias : Mapped[list["HistorialAsistencia"]] = relationship(back_populates="estudiante")
    def __repr__(self) -> str:
        return (
            f"Estudiante("
            f"id_estudiante={self.id_estudiante}, "
            f"estado='{self.estado}'"
            f")"
        )        