from sqlalchemy import Column, Integer, ForeignKey, Table, UniqueConstraint, DateTime
from sqlalchemy.sql import func
from config.database import Base

likes_table = Table('likes', Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('proyectos.id')),
    Column('fecha_creacion', DateTime, default=func.now()),  # Add this line
    UniqueConstraint('user_id', 'project_id', name='uq_user_project')
)