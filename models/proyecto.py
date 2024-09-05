from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String)
    archivo_pdf = Column(String)
    imagen = Column(String)
    usuario_nombre = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    usuario = relationship("Usuario", back_populates="proyectos")