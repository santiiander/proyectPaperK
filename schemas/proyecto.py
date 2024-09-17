from pydantic import BaseModel
from typing import Optional

class ProyectoBase(BaseModel):
    nombre: str
    descripcion: str
    archivo_pdf: str
    imagen: str
    usuario_nombre: str

class Proyecto(ProyectoBase):
    id: int
    descargas: int
    likes_count: int = 0  # Añadimos este campo para los likes

    class Config:
        from_attributes = True  # Cambiamos orm_mode a from_attributes para versiones recientes de Pydantic

class FeaturedProjects(BaseModel):
    most_liked: Optional[Proyecto] = None
    latest: Optional[Proyecto] = None