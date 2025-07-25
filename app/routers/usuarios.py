from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from app.db import SessionDep
from app.models import UsuarioDTO, Usuarios

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

@router.get("/usuarios", response_model=List[Usuarios])
async def get_usuarios(session: SessionDep):
    query = select(Usuarios)
    usuarios = session.exec(query).all()
    return usuarios
