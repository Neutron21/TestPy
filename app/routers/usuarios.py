from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Usuarios

router = APIRouter(tags=["Usuarios"])


@router.get("/usuarioByMail", response_model=Usuarios)
async def usuario_by_mail(email: str, session: SessionDep):
    query = select(Usuarios).where(Usuarios.email == email)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no existe")
    print(user)
    return user