from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Path, Query
from sqlalchemy.orm import Session
import requests
import base64
from config import database
from schemas.proyecto import ProyectoBase, Proyecto
from services.proyecto import crear_proyecto, get_proyectos, get_proyectos_por_usuario, eliminar_proyecto
from models.usuario import Usuario
from middlewares.jwt_utils import get_current_user
from middlewares.jwt_bearer import JWTBearer

router = APIRouter()

# Tu token de GitHub
GITHUB_TOKEN = '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'
GITHUB_REPO = 'santiiander/PaperKFront'  # Reemplaza con tu usuario y nombre de repositorio

def upload_to_github(file_content: bytes, file_path: str, commit_message: str, branch: str = 'main') -> bool:
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}'
    encoded_content = base64.b64encode(file_content).decode('utf-8')

    data = {
        'message': commit_message,
        'branch': branch,
        'content': encoded_content
    }

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 201

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
        # Define file paths
        pdf_path = f"{current_user.id}/{archivo_pdf.filename}"
        img_path = f"{current_user.id}/{imagen.filename}"

        # Upload files to GitHub
        pdf_uploaded = upload_to_github(archivo_pdf.file.read(), pdf_path, "Subir archivo PDF")
        img_uploaded = upload_to_github(imagen.file.read(), img_path, "Subir imagen")

        if not pdf_uploaded or not img_uploaded:
            raise HTTPException(status_code=500, detail="Error al subir archivos a GitHub")

        proyecto_data = ProyectoBase(
            nombre=nombre,
            descripcion=descripcion,
            archivo_pdf=pdf_path,  # Use the GitHub file path
            imagen=img_path  # Use the GitHub file path
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
