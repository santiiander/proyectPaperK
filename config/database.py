from sqlalchemy import create_engine
from typing import Generator
from sqlalchemy.orm import sessionmaker, declarative_base

# Cambia a mysql+mysqlconnector para usar el controlador correcto
#DATABASE_URL = "mysql+mysqlconnector://root:DILatLZGgqQCqPQnKbTnoGANnNtWifyJ@autorack.proxy.rlwy.net:13514/railway"
DATABASE_URL = "mysql+mysqlconnector://root:PcPnStgJJgiIstrYcBlPAfnEhUAVnxDF@autorack.proxy.rlwy.net:50259/railway"
#Comentarionuevo con db  test comentario xd
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
