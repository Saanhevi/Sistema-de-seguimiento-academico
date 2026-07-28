from pydantic import BaseModel


class EstudianteResponse(BaseModel):
    id: int
    nombres: str
    apellidos: str
    correo: str
    estado: bool
