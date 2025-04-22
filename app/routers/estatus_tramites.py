from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Estatus_tramites

router = APIRouter(tags=["EstatusTramites"])

@router.get("/estatus_tramites/", response_model=list[Estatus_tramites])  
async def get_all_estatus_tramite(session: SessionDep):
    query = select(Estatus_tramites)
    estatus = session.exec(query).all()

    return estatus

@router.get("/estatus_tramites/{id}", response_model=Estatus_tramites)  
async def get_estatus_tramite_by_id(id: int, session: SessionDep):
    query = select(Estatus_tramites).where(Estatus_tramites.id == id)
    estatus = session.exec(query).first()  

    if not estatus:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el estatus para este trámite")  

    return estatus