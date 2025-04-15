from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    comidas: List["Comida"] = Relationship(back_populates="usuario")

class Comida(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resultado: str
    filename: Optional[str] = None

    usuario: Usuario = Relationship(back_populates="comidas")
