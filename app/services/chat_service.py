"""
Servicios relacionados con el chat.
Proporciona funcionalidades para manejar conversaciones con el chatbot.
"""
from app.models.schemas import Usuario
from app.ai.chatbot import chatbot_service

class ChatService:
    """Servicio para gestionar conversaciones con el chatbot."""
    
    def process_message(self, mensaje: str, usuario: Usuario) -> str:
        """
        Procesa un mensaje del usuario y obtiene una respuesta del chatbot.
        
        Args:
            mensaje: Mensaje del usuario
            usuario: Usuario que envía el mensaje
            
        Returns:
            Respuesta del chatbot
        """
        # Usar el ID del usuario como identificador único de la conversación
        thread_id = str(usuario.id)
        
        # Procesar el mensaje y obtener la respuesta
        respuesta = chatbot_service.process_message(mensaje, thread_id)
        
        return respuesta