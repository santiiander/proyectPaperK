from sqlalchemy import Column, Integer, String
from config.database import Base

class Usuario(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)  # Especifica la longitud de la cadena
    hashed_password = Column(String(255))  # Especifica la longitud de la cadena
    nombre = Column(String(255))  # Especifica la longitud de la cadena
    descripcion = Column(String(255))  # Especifica la longitud de la cadena
