from sqlalchemy.orm import Session
from models.usuario import Usuario
from schemas.usuario import UsuarioCreate, UsuarioLogin

def crear_usuario(db: Session, usuario: UsuarioCreate):
    db_usuario = Usuario(
        email=usuario.email,
        hashed_password=usuario.password,  # Manejo de contraseñas sin hash
        nombre=usuario.nombre,
        descripcion=usuario.descripcion,
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def autenticar_usuario(db: Session, usuario: UsuarioLogin):
    # Buscar al usuario por email
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    
    # Verificar si el usuario existe y la contraseña es correcta
    if db_usuario and db_usuario.hashed_password == usuario.password:
        return db_usuario
    
    return None
