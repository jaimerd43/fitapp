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
from fastapi import Depends, HTTPException
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.models import Usuario
from app.db import get_session
from sqlmodel import select, Session
from pydantic import BaseModel

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

@app.get("/")
def serve_index():
    return FileResponse("./frontend/index.html")

@app.post("/procesar-foto")
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

    prompt = """
        You are a visual AI assistant specialized in nutritional analysis. Your task is to estimate the total calorie content of a meal from an image. Follow this step-by-step process:
        1. Identify the ingredients: List all recognizable food items in the image.
        2. Estimate portion sizes: For each ingredient, estimate the portion size using common units (e.g., grams, milliliters, slices, cups). Use visual cues such as the size relative to utensils, plates, or hands.
        3. Map ingredients to standard food items: Match each identified ingredient to its most relevant item in a nutritional database (e.g., "grilled chicken breast", "white rice", "olive oil").
        4. Estimate calorie content: Using standard nutritional values (e.g., kcal per 100g), estimate the calorie content of each ingredient based on the estimated portion size.
        5. Sum the total: Add up the estimated calories of each component to give a total calorie estimate for the meal.

        Please Provide a clear breakdown showing:
        - Ingredient name
        - Estimated portion size
        - Estimated calories per portion
        - Total estimated calories for the meal
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    resultado = response.output_text

    # Guardar en base de datos
    comida = Comida(
        usuario_id=usuario.id,
        resultado=resultado,
        filename=foto.filename
    )
    session.add(comida)
    session.commit()

    return {"resultado": resultado}
