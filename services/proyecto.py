from sqlalchemy.orm import Session
from models.proyecto import Proyecto
from schemas.proyecto import ProyectoBase

def crear_proyecto(db: Session, proyecto: ProyectoBase, user_id: int):
    db_proyecto = Proyecto(
        nombre=proyecto.nombre,
        descripcion=proyecto.descripcion,
        archivo_pdf=proyecto.archivo_pdf,
        imagen=proyecto.imagen,
        user_id=user_id,
        usuario_nombre=proyecto.usuario_nombre  # Usar nombre en lugar de user_id
    )
    db.add(db_proyecto)
    db.commit()
    db.refresh(db_proyecto)
    return db_proyecto

def get_proyectos(db: Session, offset: int = 0, limit: int = 10):
    return db.query(Proyecto).offset(offset).limit(limit).all()

def get_proyectos_por_usuario(db: Session, user_id: int):
    return db.query(Proyecto).filter(Proyecto.user_id == user_id).all()

def eliminar_proyecto(db: Session, proyecto_id: int, user_id: int):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id, Proyecto.user_id == user_id).first()
    if proyecto:
        db.delete(proyecto)
        db.commit()
        return proyecto
    return None
