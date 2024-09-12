from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioCreate, UsuarioLogin
from services.usuario import crear_usuario, autenticar_usuario, hash_password
from config import database
from middlewares.jwt_utils import create_access_token
from datetime import timedelta
from models.usuario import Usuario 
from services.email_service import send_reset_password_email
import random
import firebase_admin
from firebase_admin import auth
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi import Form 
from dotenv import load_dotenv

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

@router.post("/register")
async def register(usuario: UsuarioCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    user = crear_usuario(db=db, usuario=usuario)
    return {"message": "Usuario creado exitosamente", "user": user.email}

@router.post("/login")
async def login(usuario: UsuarioLogin, db: Session = Depends(database.get_db)):
    user = autenticar_usuario(db=db, usuario=usuario)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "email": user.email}

@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(database.get_db)):
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    verification_code = random.randint(100000, 999999)
    user.reset_code = verification_code
    db.commit()

    send_reset_password_email(user.email, verification_code)

    return {"msg": "Se ha enviado un código de verificación a su correo electrónico"}

@router.post("/reset-password")
async def reset_password(email: str, verification_code: int, new_password: str, db: Session = Depends(database.get_db)):
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user or user.reset_code != verification_code:
        raise HTTPException(status_code=400, detail="Código de verificación incorrecto")

    user.hashed_password = hash_password(new_password)
    user.reset_code = None
    db.commit()

    return {"msg": "Contraseña actualizada correctamente"}

class GoogleLoginRequest(BaseModel):
    id_token: str

@router.post("/login-google")
async def login_with_google(id_token: str = Form(...), db: Session = Depends(database.get_db)):
    if not id_token:
        raise HTTPException(status_code=400, detail="Token de ID no proporcionado")

    try:
        # Verificar el token de ID con Firebase
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token.get("email")

        if not email:
            raise HTTPException(status_code=400, detail="No se pudo obtener el email del token")
        
        # Verificar si el usuario ya existe en la base de datos
        user = db.query(Usuario).filter(Usuario.email == email).first()

        if user:
            # Generar un nuevo token de acceso para el usuario existente
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": user.id}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer", "email": user.email}
        
        # Si el usuario no existe, crear un nuevo usuario
        new_user_data = UsuarioCreate(
            email=email,
            password="defaultpassword",  # Puedes manejar esto de otra manera si lo prefieres
            nombre="Nombre predeterminado",
            descripcion="Descripción predeterminada"
        )
        new_user = crear_usuario(db=db, usuario=new_user_data)

        # Generar un token de acceso para el nuevo usuario
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": new_user.id}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "email": new_user.email}

    except firebase_admin.exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"Error al verificar el token de Google: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
