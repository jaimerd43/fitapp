"""
Punto de entrada principal de la aplicación.
Define la aplicación FastAPI e incluye todas las rutas y middleware necesarios.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from app import create_app

# Crear la instancia de la aplicación
app = create_app()

# Ruta raíz para servir la página principal
@app.get("/")
def serve_index():
    return FileResponse("app/static/index.html")

# Punto de entrada para ejecución directa
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)