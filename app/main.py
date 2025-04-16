import base64
import shutil
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import os
from app.db import init_db

from app.models import Comida
from fastapi import Depends, HTTPException, Body
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.models import Usuario
from app.db import get_session
from sqlmodel import select, Session
from pydantic import BaseModel
from app.chatbot import chatbot_app
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import AIMessage
from langgraph.checkpoint.base import Checkpoint
from langgraph.checkpoint.base import RunnableConfig

from app.ai.prompts import VISION_ANALYSIS_PROMPT

init_db()

app = FastAPI()

client = OpenAI()

class AuthData(BaseModel):
    email: str
    password: str

@app.post("/registro")
def registrar(data: AuthData, session: Session = Depends(get_session)):
    if session.exec(select(Usuario).where(Usuario.email == data.email)).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    user = Usuario(email=data.email, hashed_password=hash_password(data.password))
    session.add(user)
    session.commit()
    return {"mensaje": "Usuario creado"}

@app.post("/login")
def login(data: AuthData, session: Session = Depends(get_session)):
    user = session.exec(select(Usuario).where(Usuario.email == data.email)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


class AuthData(BaseModel):
    email: str
    password: str

@app.post("/registro")
def registrar(data: AuthData, session: Session = Depends(get_session)):
    if session.exec(select(Usuario).where(Usuario.email == data.email)).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    user = Usuario(email=data.email, hashed_password=hash_password(data.password))
    session.add(user)
    session.commit()
    return {"mensaje": "Usuario creado"}

@app.post("/login")
def login(data: AuthData, session: Session = Depends(get_session)):
    user = session.exec(select(Usuario).where(Usuario.email == data.email)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# Permite acceso desde cualquier origen en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

# Codifica imagen en base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Servir archivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="./frontend"), name="static")
app.mount("/static", StaticFiles(directory="./frontend"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("./frontend/index.html")
    return FileResponse("./frontend/index.html")

@app.post("/procesar-foto")
async def procesar_foto(
    foto: UploadFile = File(...),
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Guardar imagen temporal
async def procesar_foto(
    foto: UploadFile = File(...),
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Guardar imagen temporal
    temp_path = f"temp_{foto.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    # Codificar a base64
    base64_image = encode_image(temp_path)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": VISION_ANALYSIS_PROMPT},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    resultado = response.output_text
    
    # Guardar el resultado original en la sesión del usuario para poder recuperarlo después
    # Usamos un diccionario para almacenar los resultados originales por usuario
    if not hasattr(app, "resultados_originales"):
        app.resultados_originales = {}
    
    app.resultados_originales[str(usuario.id)] = resultado
    
    # Inicializar el chat con el resultado original
    chatbot_app.invoke(
        {"messages": [AIMessage(content=resultado)]},
        config={"configurable": {"thread_id": str(usuario.id)}}
    )

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return {"resultado": resultado}



@app.post("/chat")
def chat(
    mensaje: str = Body(..., embed=True),
    usuario: Usuario = Depends(get_current_user)
):
    # Config con ID único por usuario
    config = {"configurable": {"thread_id": str(usuario.id)}}
    input_msg = [HumanMessage(content=mensaje)]
    output = chatbot_app.invoke({"messages": input_msg}, config=config)

    # Devuelve solo el último mensaje generado
    respuesta = output["messages"][-1].content
    return {"respuesta": respuesta}

@app.post("/guardar-ajuste-final")
def guardar_ajuste_final(
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Usar el mismo config con thread_id
    config: RunnableConfig = {"configurable": {"thread_id": str(usuario.id)}}

    # Obtener el checkpoint actual desde el MemorySaver
    checkpoint = chatbot_app.checkpointer.get(config)

    if not checkpoint:
        raise HTTPException(status_code=404, detail="No se encontró historial para este usuario")

    # Acceder al historial de mensajes guardado
    messages = checkpoint.get("channel_values", {}).get("messages", [])
    if not messages:
        raise HTTPException(status_code=404, detail="No hay mensajes previos")

    # Contar cuántos mensajes del usuario hay para determinar si hubo ajustes
    human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
    
    # Si no hay mensajes del usuario, significa que no hubo ajustes y debemos usar el resultado original
    if len(human_messages) == 0:
        # Recuperar el resultado original guardado durante el procesamiento de la foto
        if hasattr(app, "resultados_originales") and str(usuario.id) in app.resultados_originales:
            resultado = app.resultados_originales[str(usuario.id)]
        else:
            # Si por alguna razón no tenemos el resultado original, usamos el primer mensaje AI
            ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
            if ai_messages:
                resultado = ai_messages[0].content
            else:
                raise HTTPException(status_code=404, detail="No se encontró resultado para guardar")
    else:
        # Si hay mensajes del usuario, significa que hubo ajustes y tomamos el último mensaje AI
        ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
        if ai_messages:
            resultado = ai_messages[-1].content
        else:
            raise HTTPException(status_code=404, detail="No se encontró respuesta del asistente")

    # Guardar en base de datos
    comida = Comida(
        usuario_id=usuario.id,
        resultado=resultado,
        filename="ajuste_final_chat" if len(human_messages) > 0 else "analisis_inicial"
    )
    session.add(comida)
    session.commit()

    # Limpiar el resultado original después de guardarlo (opcional)
    if hasattr(app, "resultados_originales") and str(usuario.id) in app.resultados_originales:
        del app.resultados_originales[str(usuario.id)]

    return {"mensaje": "Resultado final guardado correctamente"}


