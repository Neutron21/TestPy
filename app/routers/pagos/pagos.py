from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.db import SessionDep
from app.models import Cotizacion
from app.routers.pagos.service_pagos import manager_func


router = APIRouter(tags=["Pagos"])

@router.get("/pagos", response_model=str)
async def list_brokers(id_cotizacion: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cot_result = session.exec(query).first()
    
    if not cot_result:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    value = manager_func(cot_result.id_financiera)
    return value

