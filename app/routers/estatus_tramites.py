from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Estatus_tramites

router = APIRouter(tags=["EstatusTramites"])

@router.get("/estatus_tramites/{id}", response_model=Estatus_tramites)  
async def obtener_estatus_tramite(id: int, session: SessionDep):
    query = select(Estatus_tramites).where(Estatus_tramites.id == id)
    estatus = session.exec(query).first()  

    if not estatus:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el estatus para este trámite")  

    return estatus
@router.get("/estatus_tramites/name/{name}", response_model=int)  
async def obtener_id_estatus_tramite(name: str, session: SessionDep):
    query = select(Estatus_tramites.id).where(Estatus_tramites.name == name)
    estatus_id = session.exec(query).first()  

    if not estatus_id:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el estatus con ese nombre")  

    return estatus_id

