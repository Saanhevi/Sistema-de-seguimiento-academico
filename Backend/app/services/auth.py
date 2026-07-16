#Aquí va toda la lógica del sistema
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest
from app.models.usuario import Usuario
from app.core.security import controlador_contrasena, create_access_token
from app.repositories.usuario import UsuarioRepository

class AuthService: 
    
    def __init__(self, session: Session, repositorio:UsuarioRepository):
        self.session = session
        self.repositorio = repositorio
        
    def autenticar_usuario(self,credentials: LoginRequest) -> dict:
        """
        Busca al usuario en la base de datos, valida su contraseña y genera el JWT
        """
        with self.session as session:
            # 1. Buscamos al usuario por correo
            user = self.repositorio.buscar_por_correo(credentials.correo)
            #user = db.query(Usuario).filter(Usuario.correo==credentials.correo).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Correo o contraseña incorrectos!"
                )
            #2 Verificamos la contraseña con el controlador
            clave_correcta = controlador_contrasena.verificar_contrasena(
                credentials.password,
                user.password_hash
            )

            if not clave_correcta:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Correo o contraseña incorrectos!!"
                )
            
            # 3. Generamos el token
            token_data = {"sub": str(user.id_usuario), "rol": user.rol}
            token_real = create_access_token(data=token_data)

            # 4. Devolver el formato plano
            return{
                "access_token": token_real,
                "token_type": "bearer",
                "rol": user.rol,
                "nombres": user.nombres
            }

# def credentials_verification(credentials: LoginRequest):
#     # Simulación de base de datos
#     EMAIL_PRUEBA = "profesor@colegio.com"
#     PASSWORD_PRUEBA = "123456"

#     # Validamos las credenciales recibidas
#     if credentials.correo == EMAIL_PRUEBA and credentials.password == PASSWORD_PRUEBA:
#         return {
#             "status": "success",
#             "message": "Autenticación exitosa",
#             "user": {
#                 "nombres": "Diego",
#                 "apellidos": "Maradona",
#                 "rol": "Docente"
#             },
#             "token": "simulacion_de_token_jwt_seguro"
#         }
#     raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")