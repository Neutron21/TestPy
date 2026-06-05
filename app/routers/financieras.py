from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import List
from fastapi import APIRouter, HTTPException
from grpc import Status
from sqlmodel import select
from app.db import SessionDep
from app.models import Financieras, FinancierasDTO
from app.models import Financieras, FinancierasDTO, Utms
from sqlalchemy import text

from app.auth.security import crear_token


router = APIRouter(tags=["Financieras"])

def getFinancierasUtms(retorno: int, session):
    # 1 regresa id y nombre 0 solo regresa id
    if retorno == 1:
        query = text("""
            SELECT DISTINCT u.id_financiera, f.nombre 
            FROM financieras AS f
            INNER JOIN utms AS u ON f.id = u.id_financiera
            WHERE u.id_financiera IS NOT NULL AND u.tipo_persona IS NULL
            ORDER BY f.id
        """)
    else:
        query = text("""
            SELECT DISTINCT u.id_financiera
            FROM financieras AS f
            INNER JOIN utms AS u ON f.id = u.id_financiera
            WHERE u.id_financiera IS NOT NULL AND u.tipo_persona IS NULL
            ORDER BY f.id
        """) 
    
    result = session.exec(query).all()

    if retorno == 1:
        return result
    return [row[0] for row in result]

@router.get("/financieras", response_model=list[Financieras])
async def list_financieras(session: SessionDep):
    query = select(Financieras).where(Financieras.fase > 0).order_by(Financieras.nombre)
    financieras = session.exec(query).all()
    return financieras

@router.get("/financieras/activas", response_model=list[Financieras])
async def list_financieras_activas(session: SessionDep):
    query = select(Financieras).where(Financieras.fase.in_([1,2])).order_by(Financieras.fase, Financieras.nombre)
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


@router.get("/financieras/con-utms")
async def get_financieras_con_utms(session: SessionDep):
    
    result = getFinancierasUtms(1,session)
    # Convertimos el resultado (lista de tuplas) a una lista de diccionarios
    # row[0] es id_financiera, row[1] es el nombre
    return [{"id_financiera": row[0], "nombre": row[1]} for row in result]