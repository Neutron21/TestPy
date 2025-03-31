from fastapi import APIRouter
from sqlmodel import select
from app.db import SessionDep
from app.models import Financieras

router = APIRouter(tags=["Financieras"])


@router.get("/financieras", response_model=list[Financieras])
async def list_financieras(session: SessionDep):
    query = select(Financieras)
    financieras = session.exec(query).all()
    return financieras