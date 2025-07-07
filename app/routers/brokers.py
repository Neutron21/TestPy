from fastapi import APIRouter
from sqlmodel import select
from app.db import SessionDep
from app.models import Brokers


router = APIRouter(tags=["Brokers"])

@router.get("/brokers", response_model=list[Brokers])
async def list_brokers(session: SessionDep):
    query = select(Brokers).order_by(Brokers.nombre)
    brokers = session.exec(query).all()
    return brokers
