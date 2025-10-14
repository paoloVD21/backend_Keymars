import logging
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from app.routes import auth, user, organization
from app.config.cors import setup_cors
from app.config.settings import Settings
from app.models import auth_models, organization_models  # Importar todos los modelos
from app.utils.auth import verify_token

# Cargar configuración
settings = Settings()

# Configurar logging
logging.basicConfig(level=settings.LOG_LEVEL)
# Configurar nivel de logging específico para python_multipart
logging.getLogger("python_multipart").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Control de Inventario",
    description="Backend para gestionar el inventario de productos",
    version="0.0.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    },
    openapi_tags=[
        {"name": "auth", "description": "Operaciones de autenticación"},
        {"name": "organization", "description": "Operaciones de organización"},
    ]
)

# Configurar CORS usando la configuración centralizada
setup_cors(app)

# Configurar el esquema de seguridad OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Incluir routers
app.include_router(auth.router, prefix="/api/auth")
app.include_router(user.router)
app.include_router(organization.router, prefix="/api")