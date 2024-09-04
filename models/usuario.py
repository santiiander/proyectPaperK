from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.database import Base

class Usuario(Base):
    __tablename__ = "users"  # Debe coincidir con la clave foránea en Proyecto

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    nombre = Column(String(255))
    descripcion = Column(String(255))
    proyectos = relationship("Proyecto", back_populates="usuario")
    reset_code = Column(Integer, nullable=True)
