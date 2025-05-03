"""
Dependencias para la API de FastAPI.
Define dependencias comunes que se pueden reutilizar en múltiples rutas.
"""
from fastapi import Depends
from sqlmodel import Session

from app.db.database import get_session
from app.models.schemas import Usuario
from app.core.security import get_current_user
from app.services.food_service import FoodAnalysisService
from app.services.chat_service import ChatService

# Instancias de servicios para inyección de dependencias
food_service = FoodAnalysisService()
chat_service = ChatService()

def get_food_service() -> FoodAnalysisService:
    """
    Dependencia para obtener el servicio de análisis de comidas.
    
    Returns:
        Instancia del servicio de análisis de comidas
    """
    return food_service

def get_chat_service() -> ChatService:
    """
    Dependencia para obtener el servicio de chat.
    
    Returns:
        Instancia del servicio de chat
    """
    return chat_service

def get_db_user(
    session: Session = Depends(get_session),
    user: Usuario = Depends(get_current_user)
) -> tuple[Session, Usuario]:
    """
    Dependencia que proporciona tanto la sesión como el usuario actual.
    
    Args:
        session: Sesión de base de datos
        user: Usuario autenticado
        
    Returns:
        Tupla con la sesión y el usuario
    """
    return session, user