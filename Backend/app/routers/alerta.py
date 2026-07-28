from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_alerta_service, get_current_user, require_role
from app.schemas.alerta import AlertaCreate, AlertaResponse
from app.services.alerta import AlertaService

router = APIRouter(prefix="/api", tags=["Alertas"])


@router.post("/alertas", response_model=AlertaResponse)
def crear_alerta(
    payload: AlertaCreate,
    service: AlertaService = Depends(get_alerta_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    return service.crear_alerta(payload.id_estudiante, payload.tipo, payload.mensaje, payload.nivel, payload.id_curso)


@router.get("/alertas", response_model=list[AlertaResponse])
def listar_alertas(
    id_estudiante: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    service: AlertaService = Depends(get_alerta_service),
    usuario = Depends(get_current_user),
):
    # Si no se especifica id_estudiante, devolvemos las del usuario actual o del docente
    if id_estudiante is None:
        if usuario.rol == "Estudiante":
            return service.listar_alertas_de_estudiante(usuario.id_usuario, estado=estado)
        if usuario.rol == "Docente":
            return service.listar_alertas_para_docente(usuario.id_usuario, estado=estado)
        return []

    return service.listar_alertas_de_estudiante(id_estudiante, estado=estado)


@router.put("/alertas/{id_alerta}/vista", response_model=AlertaResponse)
def marcar_vista(id_alerta: int, service: AlertaService = Depends(get_alerta_service), usuario=Depends(get_current_user)):
    return service.marcar_vista(id_alerta, usuario)


@router.put("/alertas/{id_alerta}/atendida", response_model=AlertaResponse)
def marcar_atendida(id_alerta: int, service: AlertaService = Depends(get_alerta_service), usuario=Depends(require_role("Administrador", "Docente"))):
    return service.marcar_atendida(id_alerta, usuario)
