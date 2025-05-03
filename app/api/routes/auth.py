"""
Rutas de autenticación para la API.
Gestiona el registro e inicio de sesión de usuarios.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.models.schemas import AuthData, Token, StatusMessage, Usuario
from app.db.database import get_session
from app.db.repositories import UsuarioRepository
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(tags=["Autenticación"])

@router.post("/registro", response_model=StatusMessage)
def registrar(data: AuthData, session: Session = Depends(get_session)):
    """
    Registra un nuevo usuario en el sistema.
    
    Args:
        data: Datos de autenticación (email y contraseña)
        session: Sesión de base de datos
    
    Returns:
        Mensaje de confirmación
        
    Raises:
        HTTPException: Si el usuario ya existe
    """
    # Verificar si el usuario ya existe
    if UsuarioRepository.get_by_email(session, data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya existe")
    
    # Crear nuevo usuario
    user = Usuario(email=data.email, hashed_password=hash_password(data.password))
    UsuarioRepository.create(session, user)
    
    return StatusMessage(mensaje="Usuario creado")

@router.post("/login", response_model=Token)
def login(data: AuthData, session: Session = Depends(get_session)):
    """
    Autentica a un usuario y genera un token JWT.
    
    Args:
        data: Datos de autenticación (email y contraseña)
        session: Sesión de base de datos
        
    Returns:
        Token de acceso
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    # Buscar usuario por email
    user = UsuarioRepository.get_by_email(session, data.email)
    
    # Verificar credenciales
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    token = create_access_token({"sub": user.email})
    
    return Token(access_token=token, token_type="bearer")