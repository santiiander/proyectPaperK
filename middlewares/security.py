from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from config import database
from models.usuario import Usuario as UsuarioModel
from schemas.usuario import Usuario

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Clave secreta y algoritmo para JWT
SECRET_KEY = "your_secret_key"  # Usa una clave secreta robusta y segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Función para obtener el usuario actual a partir del token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = db.query(UsuarioModel).filter(UsuarioModel.id == user_id).first()
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user

# Función para crear un token de acceso
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
