from fastapi import FastAPI

#Inicializar la aplicación de FastAPI
app = FastAPI(
    title="API de Plataforma Académica",
    description="Servidor backend para la gesti´no de notas, asistencia y usuarios",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return{
        "status": "activo",
        "message": "Servidor de la plataforma corriendo"
    }