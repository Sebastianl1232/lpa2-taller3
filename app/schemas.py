"""Esquemas Pydantic para entradas y respuestas de la API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from utils import validar_año, validar_correo


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


class CancionCreate(BaseModel):
    """Datos necesarios para crear una canción."""

    titulo: str = Field(min_length=1, max_length=200)
    artista: str = Field(min_length=1, max_length=150)
    album: str = Field(min_length=1, max_length=150)
    duracion: int = Field(gt=0)
    año: int = Field(ge=1900)
    genero: str = Field(min_length=1, max_length=100)

    @field_validator("año")
    @classmethod
    def validar_año_cancion(cls, value: int) -> int:
        if not validar_año(value):
            raise ValueError("El año debe estar entre 1900 y el año actual")
        return value


class CancionUpdate(BaseModel):
    """Datos opcionales para actualizar una canción."""

    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    artista: str | None = Field(default=None, min_length=1, max_length=150)
    album: str | None = Field(default=None, min_length=1, max_length=150)
    duracion: int | None = Field(default=None, gt=0)
    año: int | None = Field(default=None, ge=1900)
    genero: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("año")
    @classmethod
    def validar_año_cancion(cls, value: int | None) -> int | None:
        if value is not None and not validar_año(value):
            raise ValueError("El año debe estar entre 1900 y el año actual")
        return value


class CancionResponse(BaseModel):
    """Representación pública de una canción."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    artista: str
    album: str
    duracion: int
    año: int
    genero: str
    fecha_creacion: datetime


class FavoritoCreate(BaseModel):
    """Datos necesarios para marcar una canción como favorita."""

    id_usuario: int = Field(gt=0)
    id_cancion: int = Field(gt=0)


class FavoritoResponse(BaseModel):
    """Representación pública de un favorito."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    id_usuario: int
    id_cancion: int
    fecha_marcado: datetime
