from fastapi import FastAPI
from app.routers.auth import router as auth_router #importamos el router de autenticación

app = FastAPI(
    title="API de Plataforma Académica",
    version="1.0.0"
)
app.include_router(auth_router) #incluimos el router de autenticación en la aplicación

@app.get("/")
def read_root():
    return {"status": "activo",
            "message": "La API está funcionando correctamente"
            }