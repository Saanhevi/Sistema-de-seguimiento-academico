from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.estudiante import Estudiante
from app.models.usuario import Usuario


class EstudianteService:
    def __init__(self, session: Session):
        self.session = session

    def listar(self, incluir_inactivos: bool = True) -> list[dict]:
        query = (
            self.session.query(Estudiante)
            .join(Usuario, Usuario.id_usuario == Estudiante.id_estudiante)
        )

        if not incluir_inactivos:
            query = query.filter(Estudiante.estado == "Activo")

        estudiantes = query.order_by(Usuario.apellidos, Usuario.nombres).all()

        return [
            {
                "id": estudiante.id_estudiante,
                "nombres": estudiante.usuario.nombres,
                "apellidos": estudiante.usuario.apellidos,
                "correo": estudiante.usuario.correo,
                "estado": estudiante.estado == "Activo",
            }
            for estudiante in estudiantes
        ]

    def retirar(self, id_estudiante: int) -> dict:
        estudiante = self.session.query(Estudiante).filter(Estudiante.id_estudiante == id_estudiante).first()
        if not estudiante:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")

        if estudiante.estado != "Inactivo":
            estudiante.estado = "Inactivo"
            self.session.commit()

        return {
            "id": estudiante.id_estudiante,
            "nombres": estudiante.usuario.nombres,
            "apellidos": estudiante.usuario.apellidos,
            "correo": estudiante.usuario.correo,
            "estado": False,
        }
