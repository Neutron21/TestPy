from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import List
from fastapi import APIRouter, HTTPException
from grpc import Status
from sqlmodel import select
from app.db import SessionDep
from app.models import Financieras, FinancierasDTO


router = APIRouter(tags=["Financieras"])


@router.get("/financieras", response_model=list[Financieras])
async def list_financieras(session: SessionDep):
    query = select(Financieras).where(Financieras.fase > 0).order_by(Financieras.nombre)
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

@router.post("/financiera", response_model=Financieras)
async def create_financiera(financiera_data: FinancierasDTO, session: SessionDep):
    financiera = Financieras.model_validate(financiera_data.model_dump())  
    session.add(financiera)  
    session.commit() 
    session.refresh(financiera) 
    return financiera





