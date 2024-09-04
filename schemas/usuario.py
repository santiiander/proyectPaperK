# app/schemas/usuario.py
from pydantic import BaseModel

class UsuarioBase(BaseModel):
    email: str
    nombre: str
    descripcion: str

class UsuarioCreate(BaseModel):
    email: str
    password: str
    nombre: str
    descripcion: str

class UsuarioLogin(BaseModel):
    email: str
    password: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        orm_mode = True
