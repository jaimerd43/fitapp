from typing import Literal, Dict, List, Any, Optional
import base64
import json
import pandas as pd
import os
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, END, StateGraph
from langgraph.types import Command
from openai import OpenAI
from langchain_core.tools import tool, StructuredTool

# Cliente de OpenAI
client = OpenAI()

# Función para codificar la imagen en base64 (de tu código existente)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# El prompt que ya estabas usando
NUTRITIONAL_ANALYSIS_PROMPT = """You are a visual AI assistant specialized in nutritional analysis. Your task is to estimate the total calorie content of a meal from an image. Follow this step-by-step process:
1. Identify the ingredients: List all recognizable food items in the image.
2. Estimate portion sizes: For each ingredient, estimate the portion size using common units (e.g., grams, milliliters, slices, cups). Use visual cues such as the size relative to utensils, plates, or hands.
3. Map ingredients to standard food items: Match each identified ingredient to its most relevant item in a nutritional database (e.g., "grilled chicken breast", "white rice", "olive oil").
4. Estimate calorie content: Using standard nutritional values (e.g., kcal per 100g), estimate the calorie content of each ingredient based on the estimated portion size.
5. Sum the total: Add up the estimated calories of each component to give a total calorie estimate for the meal.

Please provide ONLY a JSON response with this structure:
{
  "ingredients": [
    {
      "name": "ingredient name",
      "portion_size": "estimated portion in grams",
      "calories": estimated calories (number)
    }
  ],
  "total_calories": sum of all ingredient calories (number)
}
"""

# Función que usa tu código existente para analizar la imagen
def analyze_food_image(image_path: str) -> Dict:
    """
    Analiza una imagen de comida usando el código que ya tenías implementado.
    Retorna la información en formato estructurado.
    """
    try:
        # Codificar la imagen
        base64_image = encode_image(image_path)
        
        # Llamar a la API de OpenAI con el prompt existente
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # O el modelo que prefieras
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": NUTRITIONAL_ANALYSIS_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ]
        )
        
        # Extraer el texto de la respuesta
        analysis_text = response.choices[0].message.content
        
        # Intentar extraer el JSON de la respuesta
        try:
            # Buscar el JSON en el texto si está rodeado de ```json ... ```
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                json_str = analysis_text[json_start:json_end].strip()
                analysis_data = json.loads(json_str)
            else:
                # Intentar cargar directamente como JSON
                analysis_data = json.loads(analysis_text)
            
            return {
                "success": True,
                "analysis": analysis_data,
                "raw_text": analysis_text
            }
        except json.JSONDecodeError:
            # Si falla el parsing del JSON, devolvemos el texto para que el agente lo procese
            return {
                "success": True,
                "analysis": None,
                "raw_text": analysis_text
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_text": None
        }

# Cargar CSV de alimentos
def load_food_database(csv_path):
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        df.columns = [col.strip() for col in df.columns]
        
        # Procesar columnas según la estructura de tu CSV
        if 'Cals_per100grams' in df.columns:
            # Convertir valores como '62 cal' a números
            df['Cals_per100grams'] = pd.to_numeric(
                df['Cals_per100grams'].astype(str).str.replace('cal', '').str.strip(), 
                errors='coerce'
            )
            
        if 'KJ_per100grams' in df.columns:
            # Convertir valores como '260 kJ' a números
            df['KJ_per100grams'] = pd.to_numeric(
                df['KJ_per100grams'].astype(str).str.replace('kJ', '').str.strip(), 
                errors='coerce'
            )
            
        print(f"Base de datos cargada: {len(df)} alimentos.")
        return df
    
    except Exception as e:
        print(f"Error al cargar el CSV: {e}")
        # DataFrame básico para pruebas
        return pd.DataFrame({
            'FoodCategory': ['CannedFruit', 'CannedFruit', 'Fruits', 'Vegetables', 'Proteins'],
            'FoodItem': ['Applesauce', 'Canned Blueberries', 'Apple', 'Broccoli', 'Chicken Breast'],
            'per100grams': ['100g', '100g', '100g', '100g', '100g'],
            'Cals_per100grams': [62, 88, 52, 34, 165],
            'KJ_per100grams': [260, 370, 218, 142, 692]
        })

# Ruta al archivo CSV
csv_path = "ruta/a/tu/archivo_de_alimentos.csv"  # Reemplazar con la ruta real

# Cargar la base de datos (o usar datos de prueba para el ejemplo)
# food_db = load_food_database(csv_path)
food_db = pd.DataFrame({
    'FoodCategory': ['CannedFruit', 'CannedFruit', 'Fruits', 'Vegetables', 'Proteins'],
    'FoodItem': ['Applesauce', 'Canned Blueberries', 'Apple', 'Broccoli', 'Chicken Breast'],
    'per100grams': ['100g', '100g', '100g', '100g', '100g'],
    'Cals_per100grams': [62, 88, 52, 34, 165],
    'KJ_per100grams': [260, 370, 218, 142, 692]
})

# Función para buscar alimentos en la base de datos
def search_food_db(food_name: str) -> Dict:
    """Busca un alimento en la base de datos y devuelve sus nutrientes."""
    food_name_lower = food_name.lower()
    
    # Buscar coincidencias en el nombre del alimento
    food_data = food_db[food_db['FoodItem'].str.lower().str.contains(food_name_lower)]
    
    # Si no hay coincidencias, buscar por categoría
    if len(food_data) == 0:
        food_data = food_db[food_db['FoodCategory'].str.lower().str.contains(food_name_lower)]
    
    if len(food_data) == 0:
        return {
            "found": False,
            "message": f"No se encontró información para: {food_name}"
        }
    
    # Tomar el primer resultado
    food = food_data.iloc[0]
    
    # Extraer y procesar valores
    calories = food['Cals_per100grams']
    if isinstance(calories, str) and 'cal' in calories:
        calories = float(calories.replace('cal', '').strip())
    
    kj = food['KJ_per100grams']
    if isinstance(kj, str) and 'kJ' in kj:
        kj = float(kj.replace('kJ', '').strip())
    
    return {
        "found": True,
        "foodCategory": food['FoodCategory'],
        "foodItem": food['FoodItem'],
        "calories_per_100g": calories,
        "kj_per_100g": kj
    }

# === HERRAMIENTAS PARA EL AGENTE (USANDO LANGCHAIN TOOLS) ===

@tool
def analyze_food_image_tool(image_path: str) -> str:
    """
    Analiza una imagen de comida para identificar ingredientes y sus calorías.
    
    Args:
        image_path: Ruta a la imagen de comida
    
    Returns:
        Análisis detallado de la imagen de comida
    """
    result = analyze_food_image(image_path)
    
    if not result["success"]:
        return f"Error al analizar la imagen: {result['error']}"
    
    if result["analysis"]:
        # Si tenemos un análisis JSON estructurado
        analysis = result["analysis"]
        
        # Crear una respuesta legible
        response = "Análisis de la imagen de comida:\n\n"
        response += "Ingredientes identificados:\n"
        
        for ingredient in analysis.get("ingredients", []):
            response += f"- {ingredient['name']}: {ingredient['portion_size']}, "
            response += f"aproximadamente {ingredient['calories']} calorías\n"
        
        response += f"\nTotal estimado: {analysis.get('total_calories', 'N/A')} calorías"
        
        return response
    else:
        # Si solo tenemos texto, lo devolvemos directamente
        return f"Análisis de la imagen de comida:\n\n{result['raw_text']}"

@tool
def search_food_database(food_name: str) -> str:
    """
    Busca información nutricional de un alimento específico en nuestra base de datos.
    
    Args:
        food_name: Nombre del alimento a buscar
    
    Returns:
        Información nutricional del alimento
    """
    result = search_food_db(food_name)
    if result["found"]:
        return (f"Información para {result['foodItem']} (categoría: {result['foodCategory']}):\n"
                f"- Calorías por 100g: {result['calories_per_100g']} cal\n"
                f"- Kilojulios por 100g: {result['kj_per_100g']} kJ")
    else:
        return result["message"]

@tool
def refine_calories_with_database(ingredients: List[Dict[str, Any]]) -> str:
    """
    Refina el cálculo de calorías usando nuestra base de datos nutricional.
    
    Args:
        ingredients: Lista de ingredientes detectados con sus porciones
            [{"name": "nombre_alimento", "portion_size": "100g", "calories": 150}, ...]
    
    Returns:
        Análisis refinado con datos de nuestra base de datos
    """
    total_calories = 0
    total_kj = 0
    
    results = []
    not_found = []
    
    for item in ingredients:
        food_name = item["name"]
        
        # Convertir la porción a gramos si es necesario
        portion_str = str(item["portion_size"]).lower()
        if 'g' in portion_str:
            # Extraer número de gramos
            weight_grams = float(portion_str.replace('g', '').strip())
        elif 'ml' in portion_str:
            # Convertir ml a g (aproximación)
            weight_grams = float(portion_str.replace('ml', '').strip())
        else:
            # Si no hay unidad clara, usar el valor como está
            try:
                weight_grams = float(portion_str)
            except:
                # Si todo falla, usar 100g como valor por defecto
                weight_grams = 100
        
        # Buscar en la BD
        food_data = search_food_db(food_name)
        
        if food_data["found"]:
            # Calcular valores según el peso
            calories = (food_data["calories_per_100g"] * weight_grams) / 100
            kj = (food_data["kj_per_100g"] * weight_grams) / 100
            
            # Acumular totales
            total_calories += calories
            total_kj += kj
            
            # Añadir a resultados
            results.append({
                "food": food_data["foodItem"],
                "category": food_data["foodCategory"],
                "weight_grams": weight_grams,
                "calories": round(calories, 1),
                "kilojoules": round(kj, 1)
            })
        else:
            # Si no encontramos el alimento en nuestra BD, usar la estimación del modelo
            estimated_calories = item.get("calories", 0)
            total_calories += estimated_calories
            
            results.append({
                "food": food_name,
                "category": "Desconocido",
                "weight_grams": weight_grams,
                "calories": estimated_calories,
                "kilojoules": "N/A",
                "note": "Usando estimación del modelo (no encontrado en base de datos)"
            })
            not_found.append(food_name)
    
    # Construir respuesta
    response = "Desglose de calorías (refinado con nuestra base de datos):\n\n"
    
    for item in results:
        response += f"{item['food']} ({item['weight_grams']}g): {item['calories']} calorías"
        if 'note' in item:
            response += f" [{item['note']}]"
        response += "\n"
    
    response += f"\nTotales del plato:\n"
    response += f"- Calorías totales: {round(total_calories, 1)} cal\n"
    
    if total_kj > 0:
        response += f"- Energía total: {round(total_kj, 1)} kJ\n"
    
    if not_found:
        response += f"\nNo se encontraron en la base de datos: {', '.join(not_found)}"
        response += "\nPara estos ingredientes se usaron las estimaciones del modelo de visión."
    
    return response

# Crear el prompt para el agente
def make_system_prompt() -> str:
    return """
    Eres un asistente nutricional especializado en analizar el contenido calórico de alimentos.
    
    Tu principal tarea es ayudar a los usuarios a entender cuántas calorías contienen los platos
    de comida, ya sea a partir de descripciones textuales o de imágenes.
    
    Cuando el usuario proporcione una imagen de comida:
    1. Utiliza la herramienta 'analyze_food_image_tool' para analizar la imagen y detectar ingredientes
    2. Extrae los ingredientes identificados, sus porciones estimadas y calorías
    3. Refina esas estimaciones usando nuestra base de datos interna con 'refine_calories_with_database'
    4. Presenta los resultados de forma clara y útil
    
    Si el usuario proporciona una descripción textual del plato, identifica los ingredientes y
    busca sus valores nutricionales en la base de datos.
    
    Tu objetivo es proporcionar información nutricional precisa y útil para ayudar al usuario
    a entender el contenido calórico de sus comidas.
    
    Cuando termines tu análisis, incluye "ANÁLISIS NUTRICIONAL COMPLETO" en tu respuesta.
    """

# Configurar LLM
llm = ChatOpenAI(model="gpt-4o-mini")  # Ajustar según disponibilidad

# Crear el agente - AHORA CON HERRAMIENTAS DE LANGCHAIN
food_analysis_agent = create_react_agent(
    llm,
    tools=[
        analyze_food_image_tool,
        search_food_database,
        refine_calories_with_database
    ],
    prompt=make_system_prompt(),
)

# Nodo principal del grafo
def food_analysis_node(state: MessagesState) -> dict:
    """Nodo para analizar los alimentos y calcular calorías."""
    result = food_analysis_agent.invoke(state)
    
    # Determinar si el análisis está completo
    last_message = result["messages"][-1]
    if "ANÁLISIS NUTRICIONAL COMPLETO" in last_message.content:
        return {"messages": result["messages"], "next": END}
    
    return {"messages": result["messages"], "next": "food_analysis"}

# Construir el grafo
def build_food_analysis_graph():
    workflow = StateGraph(MessagesState)
    
    # Añadir nodo de análisis de alimentos
    workflow.add_node("food_analysis", food_analysis_node)
    
    # Configurar nodo inicial
    workflow.set_entry_point("food_analysis")
    
    # Definir transiciones condicionales
    workflow.add_conditional_edges(
        "food_analysis",
        lambda state: state["next"],
    )
    
    # Compilar el grafo
    return workflow.compile()

# Crear el agente con LangGraph
food_analyzer = build_food_analysis_graph()

# Función principal para procesar consultas y/o imágenes
def analyze_food(query=None, image_path=None):
    """
    Analiza comida a partir de una descripción textual o una imagen.
    
    Args:
        query: Descripción textual del plato (opcional)
        image_path: Ruta a la imagen del plato (opcional)
    
    Returns:
        Análisis nutricional del plato
    """
    if not query and not image_path:
        return "Por favor proporciona una descripción o una imagen de la comida."
    
    content = ""
    
    if query:
        content += query
    
    if image_path:
        if content:
            content += f"\n\nTambién he subido una imagen del plato para su análisis. La imagen está en: {image_path}"
        else:
            content = f"Por favor analiza esta imagen de comida y calcula sus calorías. La imagen está en: {image_path}"
        
        # Verificar que el archivo existe
        if not os.path.exists(image_path):
            return f"Error: No se pudo encontrar la imagen en la ruta: {image_path}"
    
    messages = [HumanMessage(content=content)]
    result = food_analyzer.invoke({"messages": messages})
    return result["messages"][-1].content

# Función simplificada para usar directamente tu código existente
def quick_analyze_image(image_path):
    """
    Función que usa directamente tu código existente sin el agente LangGraph.
    Útil para pruebas rápidas o cuando no necesitas la base de datos.
    """
    if not os.path.exists(image_path):
        return f"Error: No se pudo encontrar la imagen en la ruta: {image_path}"
    
    # Codificar la imagen
    base64_image = encode_image(image_path)
    
    # Llamar a la API de OpenAI con el prompt existente
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": NUTRITIONAL_ANALYSIS_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]
    )
    
    # Devolver el resultado
    return response.choices[0].message.content

# Ejemplo de uso
if __name__ == "__main__":

    # Ejemplo con imagen
    image_path = "/Users/jaimerd/Desktop/fitapp/images/avocado.jpg" # Reemplazar con tu ruta
    
    # Método 1: Usando el agente LangGraph completo
    print("Análisis de imagen con LangGraph:")
    print(analyze_food(image_path=image_path))
    print("\n" + "-"*50 + "\n")
