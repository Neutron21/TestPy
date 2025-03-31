from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Formatos

router = APIRouter(tags=["Formatos"])


@router.get("/formatos/{financiera_id}" , response_model=list[Formatos])
async def formatos_financiera(financiera_id: int, session: SessionDep):
    query = select(Formatos).where(Formatos.financiera_id == financiera_id)
    user = session.exec(query)
    if not user:
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formato no existe")
    print(user)
    return user