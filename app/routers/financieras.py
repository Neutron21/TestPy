from typing import List
from fastapi import APIRouter, HTTPException
from grpc import Status
from sqlmodel import select
from app.db import SessionDep
from app.models import Financieras

router = APIRouter(tags=["Financieras"])


@router.get("/financieras", response_model=list[Financieras])
async def list_financieras(session: SessionDep):
    query = select(Financieras)
    financieras = session.exec(query).all()
    return financieras
@router.get("/financieras/tipo/{tipo}", response_model=List[Financieras])
async def get_financieras_by_tipo(tipo: str, session: SessionDep):
    query = select(Financieras).where(Financieras.tipo == tipo)
    financieras = session.exec(query).all()
    if not financieras:
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="No existen Financieras con ese tipo")
    return financieras

@router.get("/financieras/fase/{fase}", response_model=List[Financieras])
async def get_financieras_by_fase(fase: int, session: SessionDep):
    query = select(Financieras).where(Financieras.fase == fase)
    financieras = session.exec(query).all()
    if not financieras:
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="No existen Financieras con esa fase")
    return financieras