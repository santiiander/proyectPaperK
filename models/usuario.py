# models/usuario.py
from sqlalchemy import Column, Integer, String
from config.database import Base

class Usuario(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    nombre = Column(String(255))
    descripcion = Column(String(255))
