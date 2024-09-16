from pydantic import BaseModel

class ProyectoBase(BaseModel):
    nombre: str
    descripcion: str
    archivo_pdf: str
    imagen: str
    usuario_nombre: str  # Agregar el campo para el nombre del usuario

class Proyecto(ProyectoBase):
    id: int
    descargas: int  # Incluye el número de descargas

    class Config:
        orm_mode = True
