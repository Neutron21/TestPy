from typing import List
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import text, select
from app.db import SessionDep
from app.models import Documentos
from sqlalchemy import and_

router = APIRouter(tags=["Documentos"])

@router.get("/documentos", response_model=List[Documentos])
async def utms_by_tipo_user_id_If(session: SessionDep, idProducto: int, tipoPersona: str = Query(None)):
   
    query = select(Documentos).where(
                and_(
                    Documentos.id_producto == idProducto,
                    Documentos.tipo_persona == tipoPersona
                ))

    result = session.exec(query).all()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documentos no encontrados")
    print(result)
    return result