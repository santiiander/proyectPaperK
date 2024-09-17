from pydantic import BaseModel
from typing import Optional

class ProyectoBase(BaseModel):
    nombre: str
    descripcion: str
    archivo_pdf: str
    imagen: str
    usuario_nombre: str
    contenido_sensible: bool

class Proyecto(ProyectoBase):
    id: int
    descargas: int
    likes_count: int = 0

    class Config:
        from_attributes = True

class FeaturedProjects(BaseModel):
    most_liked: Optional[Proyecto] = None
    latest: Optional[Proyecto] = None