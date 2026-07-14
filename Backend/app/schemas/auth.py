#Aqui se definen los esquemas de validación usando Pydantic, que nos permite validar y documentar los datos de entrada de manera sencilla
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombres: str
