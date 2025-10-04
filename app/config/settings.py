from functools import lru_cache
from pydantic import BaseModel, Field, field_validator
from typing import List
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings(BaseModel):
    """
    Configuración de la aplicación con validación y valores por defecto
    """
    # Entorno de ejecución
    ENVIRONMENT: str = Field(
        default=os.getenv("ENVIRONMENT", "development"),
        description="Entorno de ejecución (development/production)"
    )

    # Base de datos
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", ""),
        description="URL de conexión a PostgreSQL"
    )
    
    # JWT
    JWT_SECRET_KEY: str = Field(
        default=os.getenv("JWT_SECRET_KEY", ""),
        description="Clave secreta para firmar JWT"
    )
    JWT_ALGORITHM: str = Field(
        default=os.getenv("JWT_ALGORITHM", "HS256"),
        description="Algoritmo de firma JWT"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        description="Tiempo de expiración del token en minutos"
    )
    
    # Servidor
    PORT: int = Field(
        default=int(os.getenv("PORT", "8000")),
        description="Puerto del servidor"
    )
    HOST: str = Field(
        default=os.getenv("HOST", "0.0.0.0"),
        description="Host del servidor"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        description="Orígenes permitidos para CORS"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
        description="Permitir credenciales en CORS"
    )
    CORS_ALLOW_METHODS: List[str] = Field(
        default=os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(","),
        description="Métodos HTTP permitidos"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=os.getenv("CORS_ALLOW_HEADERS", "*").split(","),
        description="Headers HTTP permitidos"
    )

    # Logging
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="Nivel de logging"
    )

    # Validadores
    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str, info):
        if info.data.get("ENVIRONMENT") == "production":
            if not v or len(v) < 32:
                raise ValueError("JWT_SECRET_KEY debe tener al menos 32 caracteres en producción")
        return v

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: List[str], info):
        if info.data.get("ENVIRONMENT") == "production":
            if "*" in v:
                raise ValueError("CORS_ORIGINS no puede ser '*' en producción")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str):
        if not v:
            raise ValueError("DATABASE_URL es requerida")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración cacheada para evitar leer el archivo .env múltiples veces
    """
    return Settings(
        DATABASE_URL=os.getenv("DATABASE_URL", ""),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", ""),
        ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
        # ... otros valores desde variables de entorno
    )

# Instancia global de configuración
settings = get_settings()