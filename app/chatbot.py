from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from typing import Sequence, TypedDict
from typing_extensions import Annotated
from langgraph.graph.message import add_messages
from app.ai.prompts import CHAT_SYSTEM_PROMPT
# Define el esquema de estado
class ChatState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], add_messages]

# Configura el modelo
llm = ChatOpenAI(model="gpt-4o-mini")

# Prompt template con historial
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     CHAT_SYSTEM_PROMPT
    ),
    MessagesPlaceholder(variable_name="messages")
])

# Define el grafo
graph = StateGraph(state_schema=ChatState)

# Nodo que llama al modelo
def call_model(state: ChatState):
    prompt_value = prompt.invoke(state)
    response = llm.invoke(prompt_value)
    return {"messages": [response]}

graph.add_node("model", call_model)
graph.set_entry_point("model")

# Persistencia en memoria
memory = MemorySaver()

# Compilar app
chatbot_app = graph.compile(checkpointer=memory)
