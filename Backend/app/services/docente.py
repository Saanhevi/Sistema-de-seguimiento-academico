from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import controlador_contrasena
from app.models.docente import Docente
from app.models.usuario import Usuario


class DocenteService:
    def __init__(self, session: Session):
        self.session = session

    def listar(self) -> list[dict]:
        docentes = (
            self.session.query(Docente)
            .join(Usuario, Usuario.id_usuario == Docente.id_docente)
            .all()
        )

        return [
            {
                "id": docente.id_docente,
                "nombres": docente.usuario.nombres,
                "apellidos": docente.usuario.apellidos,
                "correo": docente.usuario.correo,
                "estado": docente.estado == "Activo",
            }
            for docente in docentes
        ]

    def crear(self, payload: dict) -> dict:
        correo_existente = self.session.query(Usuario).filter(Usuario.correo == payload["correo"]).first()
        if correo_existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está registrado")

        password_hash = controlador_contrasena.hashear(payload["password"])

        usuario = Usuario(
            nombres=payload["nombres"],
            apellidos=payload["apellidos"],
            correo=payload["correo"],
            password_hash=password_hash,
            rol="Docente",
        )
        self.session.add(usuario)
        self.session.flush()

        docente = Docente(id_docente=usuario.id_usuario, estado="Activo" if payload.get("estado", True) else "Inactivo")
        self.session.add(docente)
        self.session.commit()
        self.session.refresh(usuario)

        return {
            "id": usuario.id_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "estado": docente.estado == "Activo",
        }

    def actualizar(self, id_docente: int, payload: dict) -> dict:
        usuario = self.session.query(Usuario).filter(Usuario.id_usuario == id_docente).first()
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")

        docente = self.session.query(Docente).filter(Docente.id_docente == id_docente).first()
        if not docente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")

        correo_existente = self.session.query(Usuario).filter(Usuario.correo == payload.get("correo"), Usuario.id_usuario != id_docente).first()
        if correo_existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está registrado")

        if payload.get("nombres") is not None:
            usuario.nombres = payload["nombres"]
        if payload.get("apellidos") is not None:
            usuario.apellidos = payload["apellidos"]
        if payload.get("correo") is not None:
            usuario.correo = payload["correo"]
        if payload.get("password") is not None:
            usuario.password_hash = controlador_contrasena.hashear(payload["password"])
        if payload.get("estado") is not None:
            docente.estado = "Activo" if payload["estado"] else "Inactivo"

        self.session.commit()

        return {
            "id": usuario.id_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "estado": docente.estado == "Activo",
        }

    def cambiar_estado(self, id_docente: int, estado: bool) -> dict:
        docente = self.session.query(Docente).filter(Docente.id_docente == id_docente).first()
        if not docente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")

        docente.estado = "Activo" if estado else "Inactivo"
        self.session.commit()

        return {
            "id": docente.id_docente,
            "nombres": docente.usuario.nombres,
            "apellidos": docente.usuario.apellidos,
            "correo": docente.usuario.correo,
            "estado": docente.estado == "Activo",
        }
