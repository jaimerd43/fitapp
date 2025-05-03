"""
Rutas para el análisis de comidas.
Gestiona el procesamiento de imágenes de comida y el almacenamiento de resultados.
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlmodel import Session

from app.models.schemas import Usuario, AnalysisResponse, StatusMessage
from app.core.security import get_current_user
from app.db.database import get_session
from app.services.food_service import FoodAnalysisService
from app.api.dependencies import get_food_service

router = APIRouter(tags=["Análisis de Comidas"])

@router.post("/procesar-foto", response_model=AnalysisResponse)
async def procesar_foto(
    foto: UploadFile = File(...),
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
    food_service: FoodAnalysisService = Depends(get_food_service)
):
    """
    Procesa una imagen de comida y genera un análisis nutricional.
    
    Args:
        foto: Archivo de imagen
        usuario: Usuario autenticado
        session: Sesión de base de datos
        food_service: Servicio de análisis de comidas
        
    Returns:
        Resultado del análisis
    """
    try:
        resultado = food_service.process_food_image(foto, usuario, session)
        return AnalysisResponse(resultado=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")

@router.post("/guardar-ajuste-final", response_model=StatusMessage)
def guardar_ajuste_final(
    usuario: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
    food_service: FoodAnalysisService = Depends(get_food_service)
):
    """
    Guarda el resultado final del análisis (original o ajustado).
    
    Args:
        usuario: Usuario autenticado
        session: Sesión de base de datos
        food_service: Servicio de análisis de comidas
        
    Returns:
        Mensaje de confirmación
    """
    try:
        mensaje = food_service.save_final_analysis(usuario, session)
        return StatusMessage(mensaje=mensaje)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el resultado: {str(e)}")