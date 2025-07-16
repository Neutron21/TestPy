from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.models import Membresias
from app.db import get_session

router = APIRouter(tags=["Membresiass"])

@router.get("/membresias", response_model=list[Membresias])
def get_membresias(
    session: Session = Depends(get_session)
):
    try:
        query = select(Membresias)
        membresias = session.exec(query).all()
        return membresias
    except Exception as e:
        print("Error en get_membresias:", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")
