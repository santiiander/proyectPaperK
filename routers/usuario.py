from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioCreate, UsuarioLogin
from services.usuario import crear_usuario, autenticar_usuario, hash_password
from config import database
from middlewares.jwt_utils import create_access_token
from datetime import timedelta
from models.usuario import Usuario 
from services.email_service import send_reset_password_email  # Asegúrate de tener un servicio de email configurado
import random


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
async def login(
    usuario: UsuarioLogin,
    db: Session = Depends(database.get_db)
):
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

@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(database.get_db)):
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Generar un código de verificación como entero
    verification_code = random.randint(100000, 999999)

    # Guardar el código en la base de datos como entero
    user.reset_code = verification_code
    db.commit()

    # Enviar el correo con el código de verificación
    send_reset_password_email(user.email, verification_code)

    return {"msg": "Se ha enviado un código de verificación a su correo electrónico"}


@router.post("/reset-password")
async def reset_password(email: str, verification_code: int, new_password: str, db: Session = Depends(database.get_db)):
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user or user.reset_code != verification_code:
        raise HTTPException(status_code=400, detail="Código de verificación incorrecto")

    # Aplicar hashing a la nueva contraseña
    user.hashed_password = hash_password(new_password)
    user.reset_code = None  # Eliminar el código de verificación
    db.commit()

    return {"msg": "Contraseña actualizada correctamente"}

