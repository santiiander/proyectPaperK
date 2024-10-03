from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from config.database import Base
from models.like import likes_table
from datetime import datetime
from sqlalchemy.sql import func

class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), index=True)
    descripcion = Column(String(255))
    archivo_pdf = Column(String(255))
    imagen = Column(String(255))
    usuario_nombre = Column(String(255))
    user_id = Column(Integer, ForeignKey('users.id'))
    descargas = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    contenido_sensible = Column(Integer, default=0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="proyectos")
    liked_by_users = relationship("Usuario", secondary=likes_table, back_populates="liked_projects")