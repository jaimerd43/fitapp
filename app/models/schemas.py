
"""
Modelos de datos para la aplicación.
Define las entidades de la base de datos y los esquemas de validación.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, ForwardRef
from datetime import datetime
from pydantic import BaseModel

# Modelos para la base de datos
class Usuario(SQLModel, table=True):
    """Modelo para los usuarios de la aplicación."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    comidas: List["Comida"] = Relationship(back_populates="usuario")

class Comida(SQLModel, table=True):
    """Modelo para almacenar los análisis de comidas."""
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resultado: str
    filename: Optional[str] = None
    usuario: Usuario = Relationship(back_populates="comidas")

# Esquemas para la API
class AuthData(BaseModel):
    """Esquema para autenticación de usuarios."""
    email: str
    password: str

class Token(BaseModel):
    """Esquema para tokens de autenticación."""
    access_token: str
    token_type: str

class MessageRequest(BaseModel):
    """Esquema para mensajes del chat."""
    mensaje: str

class AnalysisResponse(BaseModel):
    """Esquema para respuestas de análisis."""
    resultado: str

class MessageResponse(BaseModel):
    """Esquema para respuestas del chat."""
    respuesta: str

class StatusMessage(BaseModel):
    """Esquema para mensajes de estado."""
    mensaje: str