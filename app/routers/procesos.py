from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from app.models import Proceso
from app.db import get_session

router = APIRouter(tags=["Procesos"])

@router.get("/procesos", response_model=list[Proceso])
def get_procesos(
    id_financiera: int,
    id_categoria: int,
    session: Session = Depends(get_session)
):
    try:
        query = select(Proceso)
        if id_financiera is not None:
            query = query.where((Proceso.id_financiera == id_financiera) & (Proceso.id_categoria == id_categoria)).order_by(Proceso.step)
        procesos = session.exec(query).all()
        return procesos
    except Exception as e:
        print("Error en get_procesos:", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")
