from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
# Aqui se guardara toda la configuracion del .env

#Directorio donde esta el .env
ruta_env = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    DATABASE_URL : str 
    SECRET_KEY : str
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    
    model_config = SettingsConfigDict(env_file=ruta_env)

settings = Settings()
