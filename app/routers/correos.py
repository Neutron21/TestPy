from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Correos

router = APIRouter(tags=["Correos"])

@router.get("/correos/{id_financiera}", response_model=list[Correos])  
async def obtener_correos(id_financiera: int, session: SessionDep):
    query = select(Correos).where(Correos.id_financiera == id_financiera)
    correos = session.exec(query).all()  

    if not correos:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron correos para esta financiera")  

    return correos  
@router.get("/correos/{id_financiera}/activos", response_model=list[Correos])  
async def obtener_correos_activos(id_financiera: int, session: SessionDep):
    query = select(Correos).where(
        (Correos.id_financiera == id_financiera) & (Correos.activo == 1)
    )
    correos = session.exec(query).all()  

    if not correos:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron correos activos para esta financiera")  

    return correos  