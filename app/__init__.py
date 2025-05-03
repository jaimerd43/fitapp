"""
Inicialización de la aplicación principal.
Este módulo importa y configura todos los componentes necesarios para la aplicación.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.database import init_db
from app.config import settings

# Función para crear y configurar la aplicación FastAPI
def create_app() -> FastAPI:
    # Inicializar la aplicación
    app = FastAPI(title=settings.APP_NAME)
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Cambia esto en producción
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Inicializar la base de datos
    init_db()
    
    # Montar archivos estáticos (frontend)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Importar e incluir rutas
    from app.api.routes import auth, food, chat
    
    # Incluir routers
    app.include_router(auth.router)
    app.include_router(food.router)
    app.include_router(chat.router)
    
    return app