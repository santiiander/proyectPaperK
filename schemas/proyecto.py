from pydantic import BaseModel

class ProyectoBase(BaseModel):
    nombre: str
    descripcion: str
    archivo_pdf: str
    imagen: str

class Proyecto(ProyectoBase):
    id: int

    class Config:
        orm_mode = True
