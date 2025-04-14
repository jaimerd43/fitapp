import base64
from openai import OpenAI

client = OpenAI()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = "/Users/jaimerd/Desktop/fitapp/images/avocado.jpg"

# Getting the Base64 string
base64_image = encode_image(image_path)


response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": """You are a visual AI assistant specialized in nutritional analysis. Your task is to estimate the total calorie content of a meal from an image. Follow this step-by-step process:
                    1. Identify the ingredients: List all recognizable food items in the image.
                    2. Estimate portion sizes: For each ingredient, estimate the portion size using common units (e.g., grams, milliliters, slices, cups). Use visual cues such as the size relative to utensils, plates, or hands.
                    3. Map ingredients to standard food items: Match each identified ingredient to its most relevant item in a nutritional database (e.g., "grilled chicken breast", "white rice", "olive oil").
                    4. Estimate calorie content: Using standard nutritional values (e.g., kcal per 100g), estimate the calorie content of each ingredient based on the estimated portion size.
                    5. Sum the total: Add up the estimated calories of each component to give a total calorie estimate for the meal.
                    
                    Please Provide a clear breakdown showing:
                    Ingredient name
                    Estimated portion size
                    Estimated calories per portion
                    Total estimated calories for the meal""" 
                 },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        }
    ],
)

print(response.output_text)