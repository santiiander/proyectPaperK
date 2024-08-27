from sqlalchemy import Column, Integer, String
from config.database import Base

class Usuario(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Asegúrate de que el nombre aquí coincida con el nombre de la columna en la base de datos
    nombre = Column(String)
    descripcion = Column(String)
