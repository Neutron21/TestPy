from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import and_
from sqlmodel import select

from app.models import Tp_producto_checklist
from app.db import SessionDep


router = APIRouter(tags=["Checklist"])


@router.get("/checklist", response_model=Tp_producto_checklist)
async def obtener_cotizaciones(
    session: SessionDep,
    producto_id: int = Query(None),
    tipo_persona: str = Query(None)):
  
    query = select(Tp_producto_checklist).where(and_(
        Tp_producto_checklist.producto_id == producto_id,
        Tp_producto_checklist.tipo_persona == tipo_persona))
    checklist = session.exec(query).first()
    
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist no encontrado")
    
    return checklist