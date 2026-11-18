"""Endpoints de estadísticas de uso."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlmodel import Session

from app.database import get_session
from app.models import Cancion, Favorito, Usuario
from app.schemas import CancionPopular, EstadisticasUso

router = APIRouter()


@router.get("/canciones/populares", response_model=list[CancionPopular])
def canciones_populares(
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    filas = session.exec(
        select(
            Cancion.id,
            Cancion.titulo,
            Cancion.artista,
            func.count(Favorito.id).label("total_favoritos"),
        )
        .join(Favorito, Favorito.id_cancion == Cancion.id)
        .group_by(Cancion.id, Cancion.titulo, Cancion.artista)
        .order_by(desc(func.count(Favorito.id)), Cancion.id)
        .limit(limit)
    ).all()

    return [
        CancionPopular(
            id=fila[0],
            titulo=fila[1],
            artista=fila[2],
            total_favoritos=int(fila[3]),
        )
        for fila in filas
    ]


@router.get("/estadisticas/uso", response_model=EstadisticasUso)
def estadisticas_uso(session: Session = Depends(get_session)):
    total_usuarios = session.scalar(select(func.count()).select_from(Usuario)) or 0
    total_canciones = session.scalar(select(func.count()).select_from(Cancion)) or 0
    total_favoritos = session.scalar(select(func.count()).select_from(Favorito)) or 0

    top = canciones_populares(limit=5, session=session)
    return EstadisticasUso(
        total_usuarios=total_usuarios,
        total_canciones=total_canciones,
        total_favoritos=total_favoritos,
        canciones_mas_favoritas=top,
    )
