from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioCreate, UsuarioLogin
from services.usuario import crear_usuario, autenticar_usuario
from config import database
from utilss.jwt_manager import create_token as create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/register")
async def register(usuario: UsuarioCreate, db: Session = Depends(database.get_db)):
    # Verificar si el usuario ya existe
    existing_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Crear nuevo usuario
    user = crear_usuario(db=db, usuario=usuario)
    return {"message": "Usuario creado exitosamente", "user": user.email}

@router.post("/login")
async def login(usuario: UsuarioLogin, db: Session = Depends(database.get_db)):
    # Verificar credenciales
    user = autenticar_usuario(db=db, usuario=usuario)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # Generar token de acceso
    access_token_expires = timedelta(minutes=30)  # Expiración del token
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "email": user.email}
