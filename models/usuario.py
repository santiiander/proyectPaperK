from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base
from models.like import likes_table

class Usuario(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    nombre = Column(String(255))
    descripcion = Column(String(255))
    proyectos = relationship("Proyecto", back_populates="usuario")
    reset_code = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now())  # Remove the comma at the end
    liked_projects = relationship("Proyecto", secondary=likes_table, back_populates="liked_by_users")