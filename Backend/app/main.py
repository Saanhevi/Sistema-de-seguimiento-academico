from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth #importamos el router de autenticación

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

app.include_router(auth.router) #incluimos el router de autenticación en la aplicación

@app.get("/")
def read_root():
    return {"status": "activo",
            "message": "La API está funcionando correctamente"
            }