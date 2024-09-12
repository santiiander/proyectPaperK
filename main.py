from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine, Base, init_db
from routers import usuario, proyecto
from fastapi.staticfiles import StaticFiles
from middlewares.jwt_bearer import JWTBearer
#from textblob import TextBlob
#cambios
app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500","https://santiiander.github.io","https://santiiander.github.io/PaperKFront/"],  # Permite solicitudes desde esta URL
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

# Inicializa la base de datos
init_db()
Base.metadata.create_all(bind=engine)

# Monta el directorio de archivos estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Incluye los routers
app.include_router(usuario.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(proyecto.router, prefix="/proyectos", tags=["Proyectos"])

# Rutas de prueba o iniciales
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de proyectos de origami"}
