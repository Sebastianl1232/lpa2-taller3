"""Endpoints REST para administrar usuarios."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlmodel import Session

from app.database import get_session
from app.models import Cancion, Favorito, Usuario
from app.schemas import (
    FavoritoResponse,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)

router = APIRouter()


@router.get("", response_model=list[UsuarioResponse])
def listar_usuarios(session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario).order_by(Usuario.id)).scalars().all()
    return usuarios


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate, session: Session = Depends(get_session)):
    existente = (
        session.exec(select(Usuario).where(Usuario.correo == datos.correo))
        .scalars()
        .first()
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese correo",
        )

    usuario = Usuario(nombre=datos.nombre, correo=datos.correo)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    session: Session = Depends(get_session),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cambios = datos.model_dump(exclude_unset=True)
    if "correo" in cambios:
        existente = (
            session.exec(
                select(Usuario).where(
                    Usuario.correo == cambios["correo"],
                    Usuario.id != usuario_id,
                )
            )
            .scalars()
            .first()
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese correo",
            )

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    session.delete(usuario)
    session.commit()


@router.get("/{usuario_id}/favoritos", response_model=list[FavoritoResponse])
def listar_favoritos_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    favoritos = (
        session.exec(
            select(Favorito)
            .where(Favorito.id_usuario == usuario_id)
            .order_by(Favorito.id)
        )
        .scalars()
        .all()
    )
    return [
        FavoritoResponse.model_validate(favorito, from_attributes=True)
        for favorito in favoritos
    ]


@router.post(
    "/{usuario_id}/favoritos/{cancion_id}",
    response_model=FavoritoResponse,
    status_code=status.HTTP_201_CREATED,
)
def marcar_favorito_usuario(
    usuario_id: int,
    cancion_id: int,
    session: Session = Depends(get_session),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cancion = session.get(Cancion, cancion_id)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    existente = (
        session.exec(
            select(Favorito).where(
                Favorito.id_usuario == usuario_id,
                Favorito.id_cancion == cancion_id,
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

    favorito = Favorito(id_usuario=usuario_id, id_cancion=cancion_id)
    session.add(favorito)
    session.commit()
    session.refresh(favorito)
    return FavoritoResponse.model_validate(favorito, from_attributes=True)


@router.delete(
    "/{usuario_id}/favoritos/{cancion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_favorito_usuario(
    usuario_id: int,
    cancion_id: int,
    session: Session = Depends(get_session),
):
    favorito = (
        session.exec(
            select(Favorito).where(
                Favorito.id_usuario == usuario_id,
                Favorito.id_cancion == cancion_id,
            )
        )
        .scalars()
        .first()
    )
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    session.delete(favorito)
    session.commit()
