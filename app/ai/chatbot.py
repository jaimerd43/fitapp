"""
Configuración del chatbot para la aplicación.
Define el flujo de conversación para ajustes en el análisis de comidas.
"""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from typing import Sequence, TypedDict, Dict, Any
from typing_extensions import Annotated
from langgraph.graph.message import add_messages

from app.ai.prompts import CHAT_SYSTEM_PROMPT
from app.config import settings

# Define el esquema de estado
class ChatState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], add_messages]

class ChatbotService:
    """Servicio para manejar conversaciones con el chatbot."""
    
    def __init__(self):
        """Inicializa el servicio del chatbot."""
        # Configura el modelo
        self.llm = ChatOpenAI(model=settings.CHAT_MODEL)
        
        # Prompt template con historial
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", CHAT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        # Define el grafo
        self.graph = StateGraph(state_schema=ChatState)
        
        # Nodo que llama al modelo
        self.graph.add_node("model", self._call_model)
        self.graph.set_entry_point("model")
        
        # Persistencia en memoria
        self.memory = MemorySaver()
        
        # Compilar app
        self.chatbot_app = self.graph.compile(checkpointer=self.memory)
    
    def _call_model(self, state: ChatState) -> Dict[str, Any]:
        """Procesa el estado actual y genera una respuesta del modelo."""
        prompt_value = self.prompt.invoke(state)
        response = self.llm.invoke(prompt_value)
        return {"messages": [response]}
    
    def process_message(self, message: str, thread_id: str) -> str:
        """
        Procesa un mensaje del usuario y obtiene una respuesta del chatbot.
        
        Args:
            message: Mensaje del usuario
            thread_id: Identificador único de la conversación
            
        Returns:
            Respuesta del chatbot
        """
        # Configuración con ID único por usuario
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        
        # Crear mensaje del usuario
        input_msg = [HumanMessage(content=message)]
        
        # Invocar el chatbot
        output = self.chatbot_app.invoke({"messages": input_msg}, config=config)
        
        # Devolver solo el último mensaje generado
        return output["messages"][-1].content
    
    def initialize_chat(self, initial_result: str, thread_id: str) -> None:
        """
        Inicializa una nueva conversación con un resultado inicial.
        
        Args:
            initial_result: Resultado inicial del análisis
            thread_id: Identificador único de la conversación
        """
        self.chatbot_app.invoke(
            {"messages": [AIMessage(content=initial_result)]},
            config={"configurable": {"thread_id": thread_id}}
        )
    
    def get_conversation_history(self, thread_id: str) -> list:
        """
        Obtiene el historial de conversación para un usuario.
        
        Args:
            thread_id: Identificador único de la conversación
            
        Returns:
            Lista de mensajes en la conversación
        """
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        checkpoint = self.chatbot_app.checkpointer.get(config)
        
        if not checkpoint:
            return []
        
        return checkpoint.get("channel_values", {}).get("messages", [])
    
    def get_final_analysis(self, thread_id: str, original_result: str) -> str:
        """
        Obtiene el análisis final basado en la conversación.
        
        Args:
            thread_id: Identificador único de la conversación
            original_result: Resultado original del análisis
            
        Returns:
            Análisis final
        """
        messages = self.get_conversation_history(thread_id)
        
        # Si no hay mensajes, usar el resultado original
        if not messages:
            return original_result
        
        # Contar cuántos mensajes del usuario hay para determinar si hubo ajustes
        human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
        
        # Si no hay mensajes del usuario, significa que no hubo ajustes
        if len(human_messages) == 0:
            return original_result
        
        # Si hay mensajes del usuario, tomar el último mensaje AI
        ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
        if ai_messages:
            return ai_messages[-1].content
        
        # Si por alguna razón no hay mensajes AI, devolver el original
        return original_result

# Instancia del servicio para usar en la aplicación
chatbot_service = ChatbotService()