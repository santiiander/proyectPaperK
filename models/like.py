from sqlalchemy import Column, Integer, ForeignKey, Table, UniqueConstraint
from config.database import Base

likes_table = Table('likes', Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('proyectos.id')),
    UniqueConstraint('user_id', 'project_id', name='uq_user_project')
)