from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router #importamos el router de autenticación
from app.routers.curso import router as curso_router
from app.routers.asistencia import router as asistencia_router
from app.core.dependencies import require_role #TODO(rbac): quitar junto con /api/whoami si ya no se necesita

app = FastAPI(
    title="API de Plataforma Académica",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router) #incluimos el router de autenticación en la aplicación
app.include_router(curso_router)
app.include_router(asistencia_router)

@app.get("/")
def read_root():
    return {"status": "activo",
            "message": "La API está funcionando correctamente"
            }

# Endpoint temporal para verificar en Swagger que RBAC (401/403) funciona.
# Quitar cuando algún módulo de dominio ya tenga un endpoint protegido real.
@app.get("/api/whoami")
def whoami(usuario = Depends(require_role("Administrador", "Docente", "Estudiante"))):
    return {
        "id_usuario": usuario.id_usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "rol": usuario.rol,
    }
