"""Modelos de persistencia de la API de música."""

from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel


class Usuario(SQLModel, table=True):
    """Representa un usuario registrado en la aplicación."""

    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    correo: str = Field(unique=True, index=True)
    fecha_registro: datetime = Field(default_factory=lambda: datetime.now(UTC))

    favoritos: list["Favorito"] = Relationship(back_populates="usuario")


class Cancion(SQLModel, table=True):
    """Representa una canción disponible en la aplicación."""

    __tablename__ = "canciones"

    id: int | None = Field(default=None, primary_key=True)
    titulo: str
    artista: str
    album: str
    duracion: int
    año: int
    genero: str
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(UTC))

    favoritos: list["Favorito"] = Relationship(back_populates="cancion")


class Favorito(SQLModel, table=True):
    """Relaciona un usuario con una canción marcada como favorita."""

    __tablename__ = "favoritos"

    id: int | None = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuarios.id")
    id_cancion: int = Field(foreign_key="canciones.id")
    fecha_marcado: datetime = Field(default_factory=lambda: datetime.now(UTC))

    usuario: Usuario | None = Relationship(back_populates="favoritos")
    cancion: Cancion | None = Relationship(back_populates="favoritos")
