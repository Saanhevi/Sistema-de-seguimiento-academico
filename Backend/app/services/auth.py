#Aquí va toda la lógica del sistema
from fastapi import HTTPException
from app.schemas.auth import LoginRequest

def credentials_verification(credentials: LoginRequest):
    # Simulación de base de datos
    EMAIL_PRUEBA = "profesor@colegio.com"
    PASSWORD_PRUEBA = "123456"

    # Validamos las credenciales recibidas
    if credentials.correo == EMAIL_PRUEBA and credentials.password == PASSWORD_PRUEBA:
        return {
            "status": "success",
            "message": "Autenticación exitosa",
            "user": {
                "nombres": "Diego",
                "apellidos": "Maradona",
                "rol": "Docente"
            },
            "token": "simulacion_de_token_jwt_seguro"
        }
    raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")