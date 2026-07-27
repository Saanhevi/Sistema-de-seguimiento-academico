#Aqui se definen los esquemas de validación usando Pydantic, que nos permite validar y documentar los datos de entrada de manera sencilla
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=1)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_usuario: int
    rol: str
    nombres: str
    apellidos: str
    id_usuario: int

class CrearCuentaEstudiantilRequest(BaseModel):
    nombres : str 
    apellidos : str 
    correo: EmailStr
    password : str = Field(min_length=1)

class ActualizarPasswordRequest(BaseModel):
    password_anterior : str = Field(min_length=1)
    password_nueva : str = Field(min_length=1)

class PerfilEstudianteResponse(BaseModel):
    id_usuario: int
    nombres: str
    apellidos: str
    correo: str
    grado_actual: str | None = None
    anio_matricula: int | None = None

class MensajeResponde(BaseModel):
    mensaje : str 