from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine, Base, init_db
from routers import usuario, proyecto
from fastapi.staticfiles import StaticFiles
from routers import auth
from fastapi import Depends
from middlewares.jwt_bearer import JWTBearer

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

init_db()

# Inicializa la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(dependencies=[Depends(JWTBearer())])

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500","http://127.0.0.1:8000"],  # Permite solicitudes desde esta URL
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)



# Incluye los routers
app.include_router(usuario.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(proyecto.router, prefix="/proyectos", tags=["Proyectos"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Rutas de prueba o iniciales
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de proyectos de origami"}
