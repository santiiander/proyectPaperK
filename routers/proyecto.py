from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Path, Query
from sqlalchemy.orm import Session
import requests
import os
from config import database
from schemas.proyecto import ProyectoBase, Proyecto
from services.proyecto import crear_proyecto, get_proyectos, get_proyectos_por_usuario, eliminar_proyecto
from models.usuario import Usuario
from middlewares.jwt_utils import get_current_user
from middlewares.jwt_bearer import JWTBearer

router = APIRouter()

API_TOKEN = "n0DA0JHfq6UmzUlIigmejhE8Jke3gVc6"
GOFILE_SERVER_URL = "https://store1.gofile.io/contents/uploadfile"  # Usa un servidor GoFile adecuado

def upload_to_gofile(file: UploadFile):
    try:
        files = {'file': (file.filename, file.file, file.content_type)}
        headers = {'Authorization': f'Bearer {API_TOKEN}'}
        
        response = requests.post(GOFILE_SERVER_URL, files=files, headers=headers)
        response_data = response.json()
        
        print("Código de estado:", response.status_code)
        print("Contenido de la respuesta:", response_data)
        
        if response_data['status'] == "ok":
            return response_data['data']['downloadPage']  # Devuelve el enlace de descarga
        else:
            raise Exception(f"Error al subir archivo: {response_data['status']}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Crear Proyecto
@router.post("/proyectos/", response_model=Proyecto, dependencies=[Depends(JWTBearer())])
def crear_proyecto_view(
    nombre: str = Form(...),
    descripcion: str = Form(...),
    archivo_pdf: UploadFile = File(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        # Subir archivos a GoFile y obtener enlaces de descarga
        pdf_link = upload_to_gofile(archivo_pdf)
        imagen_link = upload_to_gofile(imagen)
        
        proyecto_data = ProyectoBase(
            nombre=nombre,
            descripcion=descripcion,
            archivo_pdf=pdf_link,  # Usa el enlace de descarga
            imagen=imagen_link  # Usa el enlace de descarga
        )
        return crear_proyecto(db=db, proyecto=proyecto_data, user_id=current_user.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener Proyectos con Paginación
@router.get("/proyectos/traer", response_model=list[Proyecto], dependencies=[Depends(JWTBearer())])
def get_proyectos_view(
    page: int = Query(1, ge=1), 
    size: int = Query(12, ge=1), 
    db: Session = Depends(database.get_db)
):
    try:
        offset = (page - 1) * size
        proyectos = get_proyectos(db, offset=offset, limit=size)
        return proyectos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener Proyectos del Usuario Actual
@router.get("/proyectos/mi-proyecto", response_model=list[Proyecto], dependencies=[Depends(JWTBearer())])
def get_mis_proyectos_view(db: Session = Depends(database.get_db), current_user: Usuario = Depends(get_current_user)):
    try:
        result = get_proyectos_por_usuario(db, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Eliminar Proyecto
@router.delete("/proyectos/{project_id}", response_model=Proyecto, dependencies=[Depends(JWTBearer())])
def eliminar_proyecto_view(
    project_id: int = Path(..., title="ID del proyecto a eliminar"),
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        eliminado = eliminar_proyecto(db, project_id, current_user.id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return eliminado
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
