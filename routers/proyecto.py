from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Path, Query
from sqlalchemy.orm import Session
import os
from config import database
from schemas.proyecto import ProyectoBase, Proyecto
from services.proyecto import crear_proyecto, get_proyectos, get_proyectos_por_usuario, eliminar_proyecto
from models.usuario import Usuario
from middlewares.jwt_utils import get_current_user
from middlewares.jwt_bearer import JWTBearer

router = APIRouter()

# Crear Proyecto
@router.post("/proyectos/", response_model=Proyecto, dependencies=[Depends(JWTBearer())])
def crear_proyecto_view(
    usuario_nombre : str = Form(...),
    nombre: str = Form(...),
    descripcion: str = Form(...),
    archivo_pdf: UploadFile = File(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        # Define the user folder path
        user_folder = f"uploads/{current_user.id}"
        
        # Create the directory if it does not exist
        os.makedirs(user_folder, exist_ok=True)

        # Define file paths
        archivo_pdf_path = os.path.join(user_folder, archivo_pdf.filename)
        imagen_path = os.path.join(user_folder, imagen.filename)

        # Save the files to the local filesystem
        with open(archivo_pdf_path, "wb") as f:
            f.write(archivo_pdf.file.read())

        with open(imagen_path, "wb") as f:
            f.write(imagen.file.read())

        proyecto_data = ProyectoBase(
            nombre=nombre,
            descripcion=descripcion,
            archivo_pdf=archivo_pdf_path,  # Use the local file path
            imagen=imagen_path,  # Use the local file path
            usuario_nombre=usuario_nombre
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
