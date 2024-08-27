from pydantic import BaseModel

class UsuarioCreate(BaseModel):
    email: str
    password: str
    nombre: str
    descripcion: str

class UsuarioLogin(BaseModel):
    email: str
    password: str
