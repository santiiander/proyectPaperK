from sqlalchemy import create_engine
from typing import Generator
from sqlalchemy.orm import sessionmaker, declarative_base
DATABASE_URL = "mysql+mysqlconnector://root:admin@localhost:3306/paperk"
#DATABASE_URL = "mysql://root:EoKjoMdSXvhXRVqUtNOXxsrIIohDiqQT@autorack.proxy.rlwy.net:15617/railway"
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