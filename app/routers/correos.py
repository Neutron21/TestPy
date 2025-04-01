from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Correos

router = APIRouter(tags=["Correos"])

@router.get("/correos/{mail}", response_model=list[Correos])  
async def obtener_correos(mail: str, session: SessionDep):
    query = select(Correos).where(Correos.mail == mail)
    correos = session.exec(query).all()  

    if not correos:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron correos para este email")  

    return correos 
