from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.usuario import Usuario
from app.models.estudiante import Estudiante
from app.repositories.alerta import AlertaRepository


class AlertaService:

    SEVERIDAD = {"Bajo": 1, "Medio": 2, "Alto": 3}

    def __init__(self, session: Session):
        self.session = session
        self.repo = AlertaRepository(session)

    def _manejar_error(self, exc: Exception, detalle: str) -> None:
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detalle) from exc

    def _validar_estudiante(self, id_estudiante: int) -> None:
        usuario = self.session.get(Usuario, id_estudiante)
        estudiante = self.session.get(Estudiante, id_estudiante)
        if usuario is None or usuario.rol != "Estudiante" or estudiante is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El estudiante debe existir y tener rol Estudiante")

    def crear_alerta(self, id_estudiante: int, tipo: str, mensaje: str, nivel: str, id_curso: int | None = None) -> Alerta:
        try:
            self._validar_estudiante(id_estudiante)

            existente = self.repo.buscar_por_tipo_curso(id_estudiante, tipo, id_curso)
            nivel_nuevo = self.SEVERIDAD.get(nivel, 0)

            if existente:
                nivel_existente = self.SEVERIDAD.get(existente.nivel, 0)
                campos = {
                    "nivel": nivel,
                    "mensaje": mensaje,
                    "fecha": datetime.utcnow(),
                }
                if existente.estado == "Atendida":
                    campos["estado"] = "Pendiente"
                if nivel_nuevo != nivel_existente or existente.mensaje != mensaje:
                    try:
                        self.repo.actualizar_campos(existente.id_alerta, **campos)
                    except Exception as exc:
                        self._manejar_error(exc, "No se pudo actualizar la alerta existente")
                return existente

            alerta = Alerta(
                id_estudiante=id_estudiante,
                id_curso=id_curso,
                tipo=tipo,
                mensaje=mensaje,
                nivel=nivel,
                fecha=datetime.utcnow(),
                estado="Pendiente",
            )
            return self.repo.crear(alerta)
        except Exception as exc:
            self._manejar_error(exc, "No se pudo crear la alerta")

    def refrescar_alerta(self, id_estudiante: int, tipo: str, nivel: str | None, mensaje: str | None, id_curso: int | None = None) -> Alerta | None:
        try:
            if nivel is None:
                existente = self.repo.buscar_por_tipo_curso(id_estudiante, tipo, id_curso)
                if existente:
                    self.repo.borrar_por_id(existente.id_alerta)
                return None

            existente = self.repo.buscar_similar(id_estudiante, tipo, nivel, id_curso)
            if existente is None:
                return self.crear_alerta(id_estudiante, tipo, mensaje or "", nivel, id_curso=id_curso)

            nivel_nuevo = self.SEVERIDAD.get(nivel, 0)
            nivel_existente = self.SEVERIDAD.get(existente.nivel, 0)
            campos = {"nivel": nivel, "mensaje": mensaje or existente.mensaje, "fecha": datetime.utcnow()}
            if existente.estado == "Atendida":
                campos["estado"] = "Pendiente"
            if nivel_nuevo != nivel_existente or existente.mensaje != mensaje or existente.estado != "Pendiente":
                try:
                    self.repo.actualizar_campos(existente.id_alerta, **campos)
                except Exception as exc:
                    self._manejar_error(exc, "No se pudo refrescar la alerta")
            return existente
        except Exception as exc:
            self._manejar_error(exc, "No se pudo refrescar la alerta")

    def listar_alertas_de_estudiante(self, id_estudiante: int, estado: str | None = None) -> list[Alerta]:
        try:
            # Permite filtrar por estado (Pendiente, Vista, Atendida)
            return self.repo.listar_por_estudiante(id_estudiante, estado=estado)
        except Exception as exc:
            self._manejar_error(exc, "No se pudieron listar las alertas del estudiante")

    def listar_alertas_para_docente(self, id_docente: int, estado: str | None = None) -> list[Alerta]:
        try:
            return self.repo.listar_por_docente(id_docente, estado=estado)
        except Exception as exc:
            self._manejar_error(exc, "No se pudieron listar las alertas del docente")

    def marcar_vista(self, id_alerta: int, usuario_actual: Usuario) -> Alerta:
        try:
            alerta = self.repo.buscar_por_id(id_alerta)
            if not alerta:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")
            # Solo el estudiante destinatario puede marcar como vista
            if usuario_actual.rol != "Administrador" and usuario_actual.id_usuario != alerta.id_estudiante:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para marcar esta alerta")

            self.repo.actualizar_estado(id_alerta, "Vista")
            return self.repo.buscar_por_id(id_alerta)
        except Exception as exc:
            self._manejar_error(exc, "No se pudo marcar la alerta como vista")

    def marcar_atendida(self, id_alerta: int, usuario_actual: Usuario) -> Alerta:
        try:
            alerta = self.repo.buscar_por_id(id_alerta)
            if not alerta:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")
            # Solo Administrador o Docente pueden marcar como atendida
            if usuario_actual.rol not in ("Administrador", "Docente"):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para marcar esta alerta como atendida")

            self.repo.actualizar_estado(id_alerta, "Atendida")
            return self.repo.buscar_por_id(id_alerta)
        except Exception as exc:
            self._manejar_error(exc, "No se pudo marcar la alerta como atendida")
