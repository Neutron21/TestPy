from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.db import SessionDep
from app.models import Sedes

router = APIRouter(tags=["Sedes"])

@router.get("/sedes", response_model=list[Sedes])
async def list_sedes(session: SessionDep):
    sedes = session.exec(select(Sedes).order_by(Sedes.nombre)).all()
    if not sedes:
        raise HTTPException(status_code=404, detail="No hay sedes registradas")
    return sedes
