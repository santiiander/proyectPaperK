from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from models.proyecto import Proyecto
from schemas.proyecto import ProyectoBase
from models.usuario import Usuario
from models.like import likes_table
from sqlalchemy.exc import IntegrityError

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

def incrementar_descargas(db: Session, proyecto_id: int):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if proyecto:
        proyecto.descargas += 1
        db.commit()
        return proyecto
    return None

def toggle_like(db: Session, project_id: int, user_id: int):
    proyecto = db.query(Proyecto).filter(Proyecto.id == project_id).first()
    if not proyecto:
        return None
    
    like = db.query(likes_table).filter_by(user_id=user_id, project_id=project_id).first()
    
    if like:
        db.execute(likes_table.delete().where((likes_table.c.user_id == user_id) & (likes_table.c.project_id == project_id)))
        proyecto.likes_count -= 1
    else:
        try:
            db.execute(likes_table.insert().values(user_id=user_id, project_id=project_id))
            proyecto.likes_count += 1
        except IntegrityError:
            db.rollback()
            return proyecto  # El like ya existe, no hacemos nada
    
    db.commit()
    db.refresh(proyecto)
    return proyecto

def get_project_likes(db: Session, project_id: int):
    likes_count = db.query(func.count(likes_table.c.id)).filter(likes_table.c.project_id == project_id).scalar()
    if likes_count is None:
        return None
    return likes_count

# Importaciones específicas para las funciones que lo necesitan
from models.proyecto import Proyecto as ProyectoModel  # Renombramos para evitar confusión
from schemas.proyecto import Proyecto as ProyectoSchema

def get_most_liked_project(db: Session):
    return db.query(ProyectoModel).order_by(desc(ProyectoModel.likes_count)).first()

def get_latest_project(db: Session):
    return db.query(ProyectoModel).order_by(desc(ProyectoModel.id)).first()

def get_featured_projects(db: Session):
    most_liked = get_most_liked_project(db)
    latest = get_latest_project(db)
    return {
        "most_liked": ProyectoSchema.from_orm(most_liked) if most_liked else None,
        "latest": ProyectoSchema.from_orm(latest) if latest else None
    }
