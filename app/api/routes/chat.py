"""
Rutas para el chat con el asistente nutricional.
Gestiona las conversaciones entre el usuario y el chatbot.
"""
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlmodel import Session

from app.models.schemas import Usuario, MessageResponse
from app.core.security import get_current_user
from app.db.database import get_session
from app.services.chat_service import ChatService
from app.api.dependencies import get_chat_service

router = APIRouter(tags=["Chat Nutricional"])

@router.post("/chat", response_model=MessageResponse)
def chat(
    mensaje: str = Body(..., embed=True),
    usuario: Usuario = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Procesa un mensaje del usuario y obtiene una respuesta del chatbot.
    
    Args:
        mensaje: Mensaje del usuario
        usuario: Usuario autenticado
        chat_service: Servicio de chat
        
    Returns:
        Respuesta del chatbot
    """
    try:
        respuesta = chat_service.process_message(mensaje, usuario)
        return MessageResponse(respuesta=respuesta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el chat: {str(e)}")