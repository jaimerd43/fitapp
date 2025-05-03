"""
Archivo de configuración centralizada para toda la aplicación.
Permite tener variables de configuración en un solo lugar para fácil mantenimiento.
"""
import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Configuración de la base de datos
    DATABASE_URL: str = "sqlite:///db.sqlite"  # Cambiar por PostgreSQL en prod
    
    # Configuración de seguridad
    SECRET_KEY: str = "supersecreto123"  # Usar variable de entorno en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Configuración de la API de OpenAI
    OPENAI_API_KEY: str = Field(default="")
    
    # Configuración general de la aplicación
    APP_NAME: str = "Alana - Tu Asistente Nutricional"
    
    # Modelos a utilizar
    VISION_MODEL: str = "gpt-4o-mini"
    CHAT_MODEL: str = "gpt-4o-mini"
    
    # Configuración para cargar variables desde .env
    model_config = SettingsConfigDict(env_file=".env")

# Instancia de configuración para importar en otros módulos
settings = Settings()