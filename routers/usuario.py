from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioCreate, UsuarioLogin
from services.usuario import crear_usuario, autenticar_usuario
from config.database import SessionLocal
from models.usuario import Usuario

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
async def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    existing_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Crear nuevo usuario
    user = crear_usuario(db=db, usuario=usuario)
    return {"message": "Usuario creado exitosamente", "user": user.email}

@router.post("/login")
async def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):
    # Verificar credenciales
    user = autenticar_usuario(db=db, usuario=usuario)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # Aquí deberías generar un token y retornarlo
    # Por ahora, solo retornamos el email del usuario
    return {"access_token": "mocked_token", "token_type": "bearer", "email": user.email}
