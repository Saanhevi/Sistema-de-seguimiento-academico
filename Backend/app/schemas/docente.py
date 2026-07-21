from pydantic import BaseModel, Field


class DocenteCreate(BaseModel):
    nombres: str = Field(min_length=1)
    apellidos: str = Field(min_length=1)
    correo: str = Field(min_length=1)
    password: str = Field(min_length=1)
    estado: bool = True


class DocenteUpdate(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    correo: str | None = None
    password: str | None = None
    estado: bool | None = None


class DocenteEstadoUpdate(BaseModel):
    estado: bool


class DocenteResponse(BaseModel):
    id: int
    nombres: str
    apellidos: str
    correo: str
    estado: bool
    password: str | None = None
