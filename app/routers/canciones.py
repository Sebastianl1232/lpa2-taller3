"""Endpoints REST para administrar canciones."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlmodel import Session

from app.database import get_session
from app.models import Cancion
from app.schemas import CancionCreate, CancionResponse, CancionUpdate

router = APIRouter()


@router.get("", response_model=list[CancionResponse])
def listar_canciones(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    canciones = (
        session.exec(select(Cancion).order_by(Cancion.id).offset(skip).limit(limit))
        .scalars()
        .all()
    )
    return [
        CancionResponse.model_validate(cancion, from_attributes=True)
        for cancion in canciones
    ]


@router.post("", response_model=CancionResponse, status_code=status.HTTP_201_CREATED)
def crear_cancion(datos: CancionCreate, session: Session = Depends(get_session)):
    cancion = Cancion(**datos.model_dump())
    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return CancionResponse.model_validate(cancion, from_attributes=True)


@router.get("/buscar", response_model=list[CancionResponse])
def buscar_canciones(
    titulo: str | None = Query(default=None),
    artista: str | None = Query(default=None),
    genero: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    consulta = select(Cancion)
    if titulo:
        consulta = consulta.where(Cancion.titulo.ilike(f"%{titulo}%"))
    if artista:
        consulta = consulta.where(Cancion.artista.ilike(f"%{artista}%"))
    if genero:
        consulta = consulta.where(Cancion.genero.ilike(f"%{genero}%"))
    canciones = (
        session.exec(consulta.order_by(Cancion.id).offset(skip).limit(limit))
        .scalars()
        .all()
    )
    return [
        CancionResponse.model_validate(cancion, from_attributes=True)
        for cancion in canciones
    ]


@router.get("/{cancion_id}", response_model=CancionResponse)
def obtener_cancion(cancion_id: int, session: Session = Depends(get_session)):
    cancion = session.get(Cancion, cancion_id)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return CancionResponse.model_validate(cancion, from_attributes=True)


@router.put("/{cancion_id}", response_model=CancionResponse)
def actualizar_cancion(
    cancion_id: int,
    datos: CancionUpdate,
    session: Session = Depends(get_session),
):
    cancion = session.get(Cancion, cancion_id)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(cancion, campo, valor)

    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return CancionResponse.model_validate(cancion, from_attributes=True)


@router.delete("/{cancion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cancion(cancion_id: int, session: Session = Depends(get_session)):
    cancion = session.get(Cancion, cancion_id)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    session.delete(cancion)
    session.commit()
