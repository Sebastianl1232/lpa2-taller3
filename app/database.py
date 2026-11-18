"""Configuración de la conexión y sesiones de base de datos."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from musica_api.config import settings

connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=connect_args,
)


def create_db_and_tables() -> None:
    """Crea las tablas definidas por los modelos si todavía no existen."""
    from app import models

    _ = models
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    """Entrega una sesión de base de datos para una solicitud."""
    with Session(engine) as session:
        yield session
