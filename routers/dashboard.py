from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from config import database
from models.proyecto import Proyecto
from models.usuario import Usuario
from models.like import likes_table
from datetime import datetime, timedelta, date
from typing import List
from pydantic import BaseModel
import csv
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

class PublisherInfo(BaseModel):
    id: int
    email: str
    nombre: str
    project_count: int

class DashboardStats(BaseModel):
    total_projects: int
    total_likes: int
    total_users: int
    top_publishers: List[PublisherInfo]

class ProjectInfo(BaseModel):
    id: int
    nombre: str
    ruta: str

class WeeklySummary(BaseModel):
    date: str
    projects_count: int
    likes_count: int
    new_users_count: int
    projects: List[ProjectInfo]

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(database.get_db)):
    try:
        total_projects = db.query(func.count(Proyecto.id)).scalar()
        total_likes = db.query(func.count()).select_from(likes_table).scalar()
        total_users = db.query(func.count(Usuario.id)).scalar()

        top_publishers = db.query(
            Usuario.id,
            Usuario.email,
            Usuario.nombre,
            func.count(Proyecto.id).label('project_count')
        ).join(Proyecto).group_by(Usuario.id).order_by(func.count(Proyecto.id).desc()).limit(5).all()

        top_publishers_list = [
            PublisherInfo(
                id=publisher.id,
                email=publisher.email,
                nombre=publisher.nombre,
                project_count=publisher.project_count
            )
            for publisher in top_publishers
        ]

        return DashboardStats(
            total_projects=total_projects,
            total_likes=total_likes,
            total_users=total_users,
            top_publishers=top_publishers_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in get_dashboard_stats: {str(e)}")

@router.get("/dashboard/weekly-summary", response_model=List[WeeklySummary])
async def get_weekly_summary(db: Session = Depends(database.get_db)):
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

        print(f"Start date: {start_date}, End date: {end_date}")

        summary = []
        current_date = start_date

        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            print(f"Querying for date range: {current_date} to {next_date}")

            projects = db.query(Proyecto.id, Proyecto.nombre, Proyecto.user_id).filter(
                cast(Proyecto.fecha_creacion, Date) >= current_date,
                cast(Proyecto.fecha_creacion, Date) < next_date
            ).all()

            projects_info = [
                ProjectInfo(
                    id=project.id,
                    nombre=project.nombre,
                    ruta=f"https://github.com/santiiander/proyectPaperK/tree/main/uploads/{project.user_id}/{project.nombre}+%20"
                )
                for project in projects
            ]

            projects_count = len(projects)
            print(f"Projects count: {projects_count}")

            likes_count = db.query(func.count()).select_from(likes_table).filter(
                cast(likes_table.c.fecha_creacion, Date) >= current_date,
                cast(likes_table.c.fecha_creacion, Date) < next_date
            ).scalar()

            print(f"Likes count: {likes_count}")

            new_users_count = db.query(func.count(Usuario.id)).filter(
                cast(Usuario.fecha_creacion, Date) >= current_date,
                cast(Usuario.fecha_creacion, Date) < next_date
            ).scalar()

            print(f"New users count: {new_users_count}")

            summary.append(WeeklySummary(
                date=current_date.isoformat(),
                projects_count=projects_count,
                likes_count=likes_count or 0,
                new_users_count=new_users_count or 0,
                projects=projects_info
            ))

            current_date = next_date

        return summary
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_weekly_summary: {str(e)}\n\nTraceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Error in get_weekly_summary: {str(e)}")

@router.get("/dashboard/descargar-resumen-semanal")
async def descargar_resumen_semanal(db: Session = Depends(database.get_db)):
    try:
        # Obtener el resumen semanal
        resumen = await get_weekly_summary(db)

        # Crear un buffer en memoria para el CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Escribir la cabecera del CSV en español
        writer.writerow([
            "Fecha", 
            "Cantidad de Proyectos", 
            "Cantidad de Me Gusta", 
            "Nuevos Usuarios",
            "IDs de Proyectos",
            "Nombres de Proyectos",
            "Rutas de Proyectos"
        ])

        # Escribir los datos
        for dia in resumen:
            writer.writerow([
                dia.date,
                dia.projects_count,
                dia.likes_count,
                dia.new_users_count,
                ", ".join([str(p.id) for p in dia.projects]),
                ", ".join([p.nombre for p in dia.projects]),
                ", ".join([p.ruta for p in dia.projects])
            ])

        # Configurar la respuesta
        output.seek(0)
        response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=resumen_semanal.csv"

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el resumen semanal CSV: {str(e)}")
