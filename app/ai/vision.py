"""
Funcionalidades para análisis de visión con IA.
Proporciona herramientas para procesar imágenes con modelos de visión.
"""
import base64
from openai import OpenAI
from app.config import settings

# Cliente de OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def encode_image(image_path: str) -> str:
    """
    Codifica una imagen a formato base64.
    
    Args:
        image_path: Ruta al archivo de imagen
        
    Returns:
        Cadena de la imagen codificada en base64
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_food_image(image_path: str, prompt: str) -> str:
    """
    Analiza una imagen de comida utilizando el modelo de visión.
    
    Args:
        image_path: Ruta al archivo de imagen
        prompt: Instrucciones para el análisis de la imagen
        
    Returns:
        Texto con el análisis de la comida
    """
    # Codificar imagen a base64
    base64_image = encode_image(image_path)
    
    # Llamar a la API de OpenAI
    response = client.responses.create(
        model=settings.VISION_MODEL,
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
    
    return response.output_text