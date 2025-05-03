"""
Configuración de la base de datos.
Establece la conexión con la base de datos y proporciona sesiones.
"""
from sqlmodel import SQLModel, Session, create_engine
from app.config import settings

# Crear el motor de la base de datos
engine = create_engine(settings.DATABASE_URL, echo=True)

def init_db():
    """Inicializa la base de datos creando todas las tablas definidas."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Proporciona una sesión de base de datos para operaciones."""
    with Session(engine) as session:
        yield session