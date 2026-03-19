from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.db import SessionDep
from app.models import ResponsePagos
from app.routers.pagos.service_pagos import manager_func


router = APIRouter(tags=["Pagos"])

@router.get("/pagos", response_model=ResponsePagos)
async def calular_comisiones(id_cotizacion: int, session: SessionDep):
    
    return manager_func(id_cotizacion, session)

