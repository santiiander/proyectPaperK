from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config import database
from services.usuario import autenticar_usuario
from middlewares.jwt_utils import create_access_token
from schemas.usuario import UsuarioLogin
from datetime import timedelta

router = APIRouter()

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    usuario = UsuarioLogin(email=form_data.username, password=form_data.password)
    user = autenticar_usuario(db, usuario)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)  # Asumiendo 30 minutos como el tiempo de expiración
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
