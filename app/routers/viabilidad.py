from typing import List
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import text, select
from app.db import SessionDep
from app.models import Viabilidad
from sqlalchemy import and_

router = APIRouter(tags=["Viabilidad"])

@router.get("/viabilidad", response_model=List[Viabilidad])
async def utms_by_tipo_user_id_If(session: SessionDep, idProducto: int, tipoPersona: str = Query(None)):
   
    query = select(Viabilidad).where(
                and_(
                    Viabilidad.id_producto == idProducto,
                    Viabilidad.tipo_persona == tipoPersona
                ))

    result = session.exec(query).all()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viabilidad no encontrados")
    print(result)
    return result