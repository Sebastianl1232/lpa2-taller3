"""Esquemas Pydantic para entradas y respuestas de la API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from utils import validar_correo


class UsuarioCreate(BaseModel):
    """Datos necesarios para crear un usuario."""

    nombre: str = Field(min_length=1, max_length=100)
    correo: str

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value

    @field_validator("correo")
    @classmethod
    def validar_correo_usuario(cls, value: str) -> str:
        value = value.strip().lower()
        if not validar_correo(value):
            raise ValueError("Correo electrónico inválido")
        return value


class UsuarioUpdate(BaseModel):
    """Datos opcionales para actualizar un usuario."""

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    correo: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value

    @field_validator("correo")
    @classmethod
    def validar_correo_usuario(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip().lower()
        if not validar_correo(value):
            raise ValueError("Correo electrónico inválido")
        return value


class UsuarioResponse(BaseModel):
    """Representación pública de un usuario."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: str
    fecha_registro: datetime
