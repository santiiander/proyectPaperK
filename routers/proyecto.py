from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Path, Query
from sqlalchemy.orm import Session
import os
import base64
import requests
from config import database
from schemas.proyecto import FeaturedProjects, ProyectoBase, Proyecto
from services.proyecto import crear_proyecto, get_featured_projects, get_project_likes, get_proyectos, get_proyectos_por_usuario, eliminar_proyecto, get_proyectos_sensibles, incrementar_descargas, toggle_like
from models.usuario import Usuario
from middlewares.jwt_utils import get_current_user
from middlewares.jwt_bearer import JWTBearer
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Configura tu token de GitHub y el repositorio
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = 'santiiander/proyectPaperK'
GITHUB_API_URL = 'https://api.github.com/repos/{}/contents/{}'

def get_unique_filename(folder, filename):
    """
    Genera un nombre de archivo único si ya existe en la carpeta.
    """
    name, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{name}{counter}{extension}"
        counter += 1
    return new_filename

# Crear Proyecto
@router.post("/proyectos/", response_model=Proyecto, dependencies=[Depends(JWTBearer())])
def crear_proyecto_view(
    usuario_nombre: str = Form(...),
    nombre: str = Form(...),
    descripcion: str = Form(...),
    archivo_pdf: UploadFile = File(...),
    imagen: UploadFile = File(...),
    contenido_sensible: bool = Form(False),
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        # Crear una carpeta única para el proyecto
        project_folder = f"uploads/{current_user.id}/{nombre}"
        os.makedirs(project_folder, exist_ok=True)

        # Generar nombres únicos para los archivos
        archivo_pdf_filename = get_unique_filename(project_folder, archivo_pdf.filename)
        imagen_filename = get_unique_filename(project_folder, imagen.filename)

        # Definir las rutas de los archivos
        archivo_pdf_path = os.path.join(project_folder, archivo_pdf_filename)
        imagen_path = os.path.join(project_folder, imagen_filename)

        # Guardar los archivos en el sistema de archivos local
        with open(archivo_pdf_path, "wb") as f:
            f.write(archivo_pdf.file.read())

        with open(imagen_path, "wb") as f:
            f.write(imagen.file.read())

        # Subir archivos a GitHub
        def upload_to_github(local_path, repo_path):
            # Revisa si el archivo ya existe en GitHub
            url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}'
            headers = {
                'Authorization': f'token {GITHUB_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            # Intentar obtener la información del archivo para ver si ya existe
            response = requests.get(url, headers=headers)
            file_exists = response.status_code == 200
            
            with open(local_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')  # Codificar contenido a base64
            
            if file_exists:
                # Obtener el sha del archivo existente para actualizarlo
                file_info = response.json()
                sha = file_info['sha']
                json_data = {
                    'message': f'Update {repo_path}',
                    'content': content,
                    'sha': sha
                }
            else:
                # Crear el archivo si no existe
                json_data = {
                    'message': f'Add {repo_path}',
                    'content': content
                }
            
            # Subir el archivo a GitHub
            response = requests.put(url, headers=headers, json=json_data)
            if response.status_code not in [200, 201]:
                raise HTTPException(status_code=response.status_code, detail=response.text)

        # Definir las rutas de GitHub
        archivo_pdf_github_path = f"{project_folder}/{archivo_pdf_filename}"
        imagen_github_path = f"{project_folder}/{imagen_filename}"

        # Subir archivos a GitHub
        upload_to_github(archivo_pdf_path, archivo_pdf_github_path)
        upload_to_github(imagen_path, imagen_github_path)

        proyecto_data = ProyectoBase(
            nombre=nombre,
            descripcion=descripcion,
            archivo_pdf=archivo_pdf_github_path,
            imagen=imagen_github_path,
            usuario_nombre=usuario_nombre,
            contenido_sensible=contenido_sensible
        )
        return crear_proyecto(db=db, proyecto=proyecto_data, user_id=current_user.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/proyectos/sensibles", response_model=list[Proyecto], dependencies=[Depends(JWTBearer())])
def get_proyectos_sensibles_view(
    page: int = Query(1, ge=1), 
    size: int = Query(12, ge=1), 
    db: Session = Depends(database.get_db)
):
    try:
        offset = (page - 1) * size
        proyectos = get_proyectos_sensibles(db, offset=offset, limit=size)
        return proyectos
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

@router.post("/proyectos/{project_id}", response_model=Proyecto)
def incrementar_descarga(
    project_id: int = Path(..., title="ID del proyecto"),
    db: Session = Depends(database.get_db)
):
    try:
        # Incrementar el contador de descargas
        proyecto = incrementar_descargas(db, project_id)
        
        if not proyecto:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")

        # Convertir el proyecto a un esquema Pydantic para la respuesta
        return proyecto

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/proyectos/{project_id}/like", response_model=Proyecto, dependencies=[Depends(JWTBearer())])
def toggle_like_proyecto(
    project_id: int = Path(..., title="ID del proyecto"),
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        proyecto = toggle_like(db, project_id, current_user.id)
        if not proyecto:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return proyecto
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/proyectos/{project_id}/likes", response_model=int, dependencies=[Depends(JWTBearer())])
def get_proyecto_likes(
    project_id: int = Path(..., title="ID del proyecto"),
    db: Session = Depends(database.get_db)
):
    try:
        likes = get_project_likes(db, project_id)
        if likes is None:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return likes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/proyectos/destacados", response_model=FeaturedProjects, dependencies=[Depends(JWTBearer())])
def get_proyectos_destacados(db: Session = Depends(database.get_db)):
    try:
        featured_projects = get_featured_projects(db)
        return FeaturedProjects(**featured_projects)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))