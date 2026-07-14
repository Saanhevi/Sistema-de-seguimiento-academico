from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings #importamos variables de .env

class ControladorContrasena: 
    password_hash = PasswordHash.recommended()
    
    def hashear(self, contrasena_plana):
        return self.password_hash.hash(contrasena_plana) #Retorna la contrasena hasheada
    
    def verificar_contrasena(self, contrasena_plana, hash_guardado):
        # Retorna true si la contrasena es correcta
        return self.password_hash.verify(contrasena_plana, hash_guardado)
    
controlador_contrasena = ControladorContrasena()

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Genera un token JWT firmado y seguro usando la configuración del equipo
    """
    # 1. Sacamos una copia limpia de los datos que queremos guardar dentro del token
    to_encode = data.copy()
    # 2. Si definimos un tiempo de expiración al usar la función, lo aplicamos
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 3. Añadimos laf recha de vencimiento al diccionario con la clave estándar "exp"
    to_encode.update({"exp": expire})

    # 4. Encriptamos los datos usando la SECRET_KEY y el ALGORITHM de config.py
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # 5. Devolvemos el token encriptado como un texto plano largo
    return encoded_jwt