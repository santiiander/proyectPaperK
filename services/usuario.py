import bcrypt
from sqlalchemy.orm import Session
from models.usuario import Usuario
from schemas.usuario import UsuarioCreate, UsuarioLogin

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def crear_usuario(db: Session, usuario: UsuarioCreate):
    hashed_password = hash_password(usuario.password)
    db_usuario = Usuario(
        email=usuario.email,
        hashed_password=hashed_password,
        nombre=usuario.nombre,
        descripcion=usuario.descripcion,
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def autenticar_usuario(db: Session, usuario: UsuarioLogin):
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario and verify_password(usuario.password, db_usuario.hashed_password):
        return db_usuario
    return None
