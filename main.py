import logging
import uvicorn
from fastapi import FastAPI
from app.routes import auth
from app.config.cors import setup_cors
from app.config.settings import Settings

# Cargar configuración
settings = Settings()

# Configurar logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Control de Inventario",
    description="Backend para gestionar el inventario de productos",
    version="0.0.0"
)

# Configurar CORS usando la configuración centralizada
setup_cors(app)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth")