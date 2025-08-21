from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import text
from app.db import SessionDep
from app.models import Utms

router = APIRouter(tags=["Utms"])

@router.get("/utms", response_model=Utms)
async def utms_by_tipo_user_id_If(session: SessionDep, idFin: int, idUsuario: Optional[int] = Query(None), tipoPersona: Optional[str] = Query(None)):

    query_filters = ""
    params = {}

    if idFin is not None:
        query_filters += " AND id_financiera = :id_financiera"
        params["id_financiera"] = idFin

    if idUsuario is not None:
        query_filters += " AND id_usuario = :id_usuario"
        params["id_usuario"] = idUsuario

    if tipoPersona is not None:
        query_filters += " AND tipo_persona = :tipo_persona"
        params["tipo_persona"] = tipoPersona

    query = f"""
        SELECT * FROM utms
        WHERE 1=1
        {query_filters}
        """
    result = session.execute(text(query), params).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utm no encontrada")
    print(result)
    return result