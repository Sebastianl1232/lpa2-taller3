"""
Configuración de la aplicación.
Maneja diferentes entornos: desarrollo, pruebas y producción.
"""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Lee las variables de entorno desde el archivo .env
    """

    # Configuración básica de la aplicación
    app_name: str = "API de Música"
    app_version: str = "1.0.0"

    # Configuración del entorno
    environment: Literal["development", "testing", "production"] = "development"

    # Configuración de la base de datos
    # Para SQLite: sqlite:///./musica.db
    # Para PostgreSQL: postgresql://user:password@localhost/dbname
    database_url: str = Field(default="sqlite:///./musica.db", min_length=1)

    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = True

    # Configuración de CORS
    # En desarrollo puedes usar ["*"], en producción especifica los orígenes permitidos
    cors_origins: list[str] = ["*"]

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Valida que la URL de base de datos tenga un esquema soportado."""
        if "://" not in value:
            raise ValueError(
                "DATABASE_URL debe incluir un esquema, por ejemplo sqlite:///"
            )
        return value


# Crear una instancia global de Settings
settings = Settings()


# Crear diferentes configuraciones para cada entorno
class DevelopmentSettings(Settings):
    """Configuración para el entorno de desarrollo."""

    environment: Literal["development"] = "development"
    debug: bool = True


class TestingSettings(Settings):
    """Configuración para el entorno de pruebas."""

    __test__ = False
    environment: Literal["testing"] = "testing"
    # Usar una base de datos diferente para pruebas
    database_url: str = "sqlite:///./test_musica.db"


class ProductionSettings(Settings):
    """Configuración para el entorno de producción."""

    environment: Literal["production"] = "production"
    debug: bool = False


# Función para obtener la configuración según el entorno
def get_settings() -> Settings:
    """
    Retorna la configuración apropiada según el entorno.
    """
    env = settings.environment.lower()

    if env == "testing":
        return TestingSettings()
    elif env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()
