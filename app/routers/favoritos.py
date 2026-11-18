"""Endpoints REST para administrar favoritos."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlmodel import Session

from app.database import get_session
from app.models import Cancion, Favorito, Usuario
from app.schemas import FavoritoCreate, FavoritoResponse

router = APIRouter()


def crear_favorito_para_ids(
    id_usuario: int,
    id_cancion: int,
    session: Session,
) -> Favorito:
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cancion = session.get(Cancion, id_cancion)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    existente = (
        session.exec(
            select(Favorito).where(
                Favorito.id_usuario == id_usuario,
                Favorito.id_cancion == id_cancion,
            )
        )
        .scalars()
        .first()
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La canción ya está marcada como favorita",
        )

    favorito = Favorito(id_usuario=id_usuario, id_cancion=id_cancion)
    session.add(favorito)
    session.commit()
    session.refresh(favorito)
    return favorito


@router.get("", response_model=list[FavoritoResponse])
def listar_favoritos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    favoritos = (
        session.exec(select(Favorito).order_by(Favorito.id).offset(skip).limit(limit))
        .scalars()
        .all()
    )
    return [
        FavoritoResponse.model_validate(favorito, from_attributes=True)
        for favorito in favoritos
    ]


@router.post("", response_model=FavoritoResponse, status_code=status.HTTP_201_CREATED)
def crear_favorito(
    datos: FavoritoCreate,
    session: Session = Depends(get_session),
):
    favorito = crear_favorito_para_ids(datos.id_usuario, datos.id_cancion, session)
    return FavoritoResponse.model_validate(favorito, from_attributes=True)


@router.get("/{favorito_id}", response_model=FavoritoResponse)
def obtener_favorito(favorito_id: int, session: Session = Depends(get_session)):
    favorito = session.get(Favorito, favorito_id)
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    return FavoritoResponse.model_validate(favorito, from_attributes=True)


@router.delete("/{favorito_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_favorito(favorito_id: int, session: Session = Depends(get_session)):
    favorito = session.get(Favorito, favorito_id)
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    session.delete(favorito)
    session.commit()
