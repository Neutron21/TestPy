from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from app.models import Proceso
from app.db import get_session

router = APIRouter(tags=["Procesos"])

@router.get("/procesos", response_model=list[Proceso])
def get_procesos(
    id_financiera: Optional[int] = None,
    session: Session = Depends(get_session)
):
    try:
        query = select(Proceso)
        if id_financiera is not None:
            query = query.where(Proceso.id_financiera == id_financiera)
        procesos = session.exec(query).all()
        return procesos
    except Exception as e:
        print("Error en get_procesos:", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")
