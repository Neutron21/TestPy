from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, text
from app.db import SessionDep
from app.models import UsuarioDTO, UsuarioResponse, UsuarioSimple, Usuarios

router = APIRouter(tags=["Usuarios"])


@router.get("/usuarioByMail", response_model=Usuarios)
async def usuario_by_mail(email: str, session: SessionDep):
    query = select(Usuarios).where(Usuarios.email == email)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no existe")
    print(user)
    return user

@router.post("/usuarios", response_model=Usuarios) 
async def create_usuario(usuario_data: UsuarioDTO, session: SessionDep):
    usuario = Usuarios.model_validate(usuario_data.model_dump())  
    session.add(usuario)  
    session.commit() 
    session.refresh(usuario) 
    return usuario  

@router.get("/usuarios", response_model=List[UsuarioResponse])
async def get_usuarios(session: SessionDep):
    query = select(Usuarios)
    usuarios = session.exec(query).all()
    return usuarios

@router.get("/usuarios/subordinados", response_model=list[UsuarioSimple])
async def list_brokers(id_user: int, session: SessionDep):
    queryUser = select(Usuarios).where(Usuarios.id == id_user)
    user = session.exec(queryUser).first()
    print(user)
    if user.rol == 'a':
        query = select(Usuarios.id, Usuarios.nombre)
        result = session.exec(query).all()
    else: 
        query = text("""
            WITH RECURSIVE subordinates AS (
                SELECT id, id_broker FROM usuarios WHERE id = :user_id
                UNION ALL
                SELECT u.id, u.id_broker
                FROM usuarios u
                INNER JOIN subordinates s ON u.id_superior = s.id
            )
            SELECT id, nombre FROM usuarios WHERE id IN (SELECT id FROM subordinates)
            ORDER BY nombre         
            """)
    result = session.execute(query, {"user_id": id_user})

    return result