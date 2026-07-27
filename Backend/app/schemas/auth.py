#Aqui se definen los esquemas de validación usando Pydantic, que nos permite validar y documentar los datos de entrada de manera sencilla
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.identidad import normalizar_documento

# Lo que se guarda en Usuario.documento: ya sin separadores y dentro de VARCHAR(20).
_DOCUMENTO_NORMALIZADO = re.compile(r"^[0-9A-Za-z]{5,20}$")

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
    # HU22: obligatorio en el formulario aunque la columna sea nullable en la BD.
    # No es contradictorio: los usuarios que ya existen no tienen documento y
    # obligarlo en el esquema exigiría rellenar filas con datos falsos.
    # Se acepta alfanumérico porque las cédulas de extranjería y los pasaportes
    # llevan letras. Los separadores se quitan antes de guardar (RN-r), así que
    # el documento almacenado tiene exactamente la misma forma que el que llegará
    # desde un Excel: si se guarda "1.023.456.789" y se busca "1023456789", el
    # emparejamiento no falla, simplemente no encuentra a nadie.
    documento : str = Field(min_length=5, max_length=20)
    password : str = Field(min_length=1)

    @field_validator("documento")
    @classmethod
    def _normalizar_documento(cls, valor: str) -> str:
        normalizado = normalizar_documento(valor)
        if not normalizado or not _DOCUMENTO_NORMALIZADO.match(normalizado):
            raise ValueError("El documento debe tener entre 5 y 20 caracteres alfanuméricos")
        return normalizado

class ActualizarPasswordRequest(BaseModel):
    password_anterior : str = Field(min_length=1)
    password_nueva : str = Field(min_length=1)

class PerfilEstudianteResponse(BaseModel):
    id_usuario: int
    nombres: str
    apellidos: str
    correo: str
    documento: str | None = None
    grado_actual: str | None = None
    anio_matricula: int | None = None

class MensajeResponde(BaseModel):
    mensaje : str 