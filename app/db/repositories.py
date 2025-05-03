"""
Repositorios para operaciones de base de datos.
Proporciona funciones de acceso a datos de manera estructurada.
"""
from sqlmodel import Session, select
from app.models.schemas import Usuario, Comida

class UsuarioRepository:
    """Repositorio para operaciones relacionadas con usuarios."""
    
    @staticmethod
    def get_by_email(session: Session, email: str) -> Usuario:
        """Obtiene un usuario por su email."""
        return session.exec(select(Usuario).where(Usuario.email == email)).first()
    
    @staticmethod
    def create(session: Session, usuario: Usuario) -> Usuario:
        """Crea un nuevo usuario."""
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario

class ComidaRepository:
    """Repositorio para operaciones relacionadas con análisis de comidas."""
    
    @staticmethod
    def create(session: Session, comida: Comida) -> Comida:
        """Guarda un nuevo análisis de comida."""
        session.add(comida)
        session.commit()
        session.refresh(comida)
        return comida
    
    @staticmethod
    def get_by_usuario_id(session: Session, usuario_id: int) -> list[Comida]:
        """Obtiene todos los análisis de comida de un usuario."""
        return session.exec(select(Comida).where(Comida.usuario_id == usuario_id)).all()
    
    @staticmethod
    def get_by_id(session: Session, comida_id: int) -> Comida:
        """Obtiene un análisis de comida por su ID."""
        return session.exec(select(Comida).where(Comida.id == comida_id)).first()