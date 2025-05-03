"""
Utilidades generales para la aplicación.
Proporciona funciones de ayuda usadas en diferentes partes de la aplicación.
"""
import os
import logging
from datetime import datetime

# Configuración de logging
def setup_logger(name):
    """
    Configura un logger con un formato específico.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Instancia de logger configurada
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Crear handler para consola
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        
        # Definir formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger

# Logger para la aplicación
app_logger = setup_logger("alana")

def ensure_directory_exists(directory):
    """
    Asegura que un directorio existe, creándolo si es necesario.
    
    Args:
        directory: Ruta del directorio
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_temp_filename(original_filename):
    """
    Genera un nombre de archivo temporal único basado en el nombre original.
    
    Args:
        original_filename: Nombre de archivo original
        
    Returns:
        Nombre de archivo temporal único
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    base_name = os.path.splitext(original_filename)[0]
    extension = os.path.splitext(original_filename)[1]
    return f"temp_{base_name}_{timestamp}{extension}"