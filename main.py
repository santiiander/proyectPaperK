from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine, Base, init_db
from routers import usuario, proyecto, dashboard
from fastapi.staticfiles import StaticFiles
from middlewares.jwt_bearer import JWTBearer
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la configuración de Firebase desde las variables de entorno
firebase_config = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),  # Asegúrate de reemplazar \n por saltos de línea
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
}

# Inicializar Firebase
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])

# Rutas de prueba o iniciales
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de proyectos de origami"}


@app.get("/firebase-config")
async def get_firebase_config():
    return {
        "apiKey": os.getenv("apiKey"),
        "authDomain": os.getenv("authDomain"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("storageBucket"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("appId"),
        "measurementId": os.getenv("measurementId")
    }