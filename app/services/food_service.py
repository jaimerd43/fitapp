"""
Servicios relacionados con el análisis de comidas.
Proporciona funcionalidades para procesar y almacenar análisis de comidas.
"""
import os
import shutil
from sqlmodel import Session
from fastapi import UploadFile

from app.models.schemas import Comida, Usuario
from app.db.repositories import ComidaRepository
from app.ai.vision import analyze_food_image
from app.ai.prompts import VISION_ANALYSIS_PROMPT
from app.ai.chatbot import chatbot_service

class FoodAnalysisService:
    """Servicio para el análisis de comidas."""
    
    def __init__(self):
        """Inicializa el servicio de análisis de comidas."""
        # Diccionario para almacenar resultados originales por usuario
        self.resultados_originales = {}
    
    def process_food_image(self, foto: UploadFile, usuario: Usuario, session: Session) -> str:
        """
        Procesa una imagen de comida y genera un análisis.
        
        Args:
            foto: Archivo de imagen subido
            usuario: Usuario que realiza la solicitud
            session: Sesión de base de datos
            
        Returns:
            Resultado del análisis
        """
        # Guardar imagen temporal
        temp_path = f"temp_{foto.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        
        try:
            # Analizar la imagen
            resultado = analyze_food_image(temp_path, VISION_ANALYSIS_PROMPT)
            
            # Guardar el resultado original para este usuario
            self.resultados_originales[str(usuario.id)] = resultado
            
            # Inicializar el chat con el resultado original
            chatbot_service.initialize_chat(resultado, str(usuario.id))
            
            return resultado
        finally:
            # Limpiar archivos temporales
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def save_final_analysis(self, usuario: Usuario, session: Session) -> str:
        """
        Guarda el análisis final en la base de datos.
        
        Args:
            usuario: Usuario que realiza la solicitud
            session: Sesión de base de datos
            
        Returns:
            Mensaje de confirmación
        """
        # Obtener el resultado original para este usuario
        original_result = self.resultados_originales.get(str(usuario.id))
        
        # Obtener el análisis final basado en la conversación
        resultado_final = chatbot_service.get_final_analysis(str(usuario.id), original_result)
        
        # Determinar si hubo ajustes
        messages = chatbot_service.get_conversation_history(str(usuario.id))
        human_messages = [msg for msg in messages if isinstance(msg, type) and msg.__name__ == "HumanMessage"]
        
        # Guardar en base de datos
        comida = Comida(
            usuario_id=usuario.id,
            resultado=resultado_final,
            filename="ajuste_final_chat" if human_messages else "analisis_inicial"
        )
        
        ComidaRepository.create(session, comida)
        
        # Limpiar el resultado original después de guardarlo
        if str(usuario.id) in self.resultados_originales:
            del self.resultados_originales[str(usuario.id)]
        
        return "Análisis guardado correctamente"