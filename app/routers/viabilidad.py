from typing import List
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import text, select
from app.db import SessionDep
from app.models import Viabilidad
from sqlalchemy import and_

router = APIRouter(tags=["Viabilidad"])

@router.get("/viabilidad", response_model=List[Viabilidad])
async def get_Viiabilidad_by_If_and_TipoPersona(session: SessionDep, idProducto: int, tipoPersona: str = Query(None)):
    try:
        query = select(Viabilidad).where(
                    and_(
                        Viabilidad.id_producto == idProducto,
                        Viabilidad.tipo_persona == tipoPersona
                    ))
        result = []
        result = session.exec(query).all()

        return result
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor", error=e)
    
@router.get("/viabilidad/group")
async def get_Viiabilidad_by_If_and_TipoPersona_Group(session: SessionDep, idProducto: int, tipoPersona: str = Query(None)):
    try:
        query = select(Viabilidad).where(
                    and_(
                        Viabilidad.id_producto == idProducto,
                        Viabilidad.tipo_persona == tipoPersona
                    ))
        data = []
        data = session.exec(query).all()

        result = {}
        for item in data:
            key = item.responsable
            # if not key:  
            #     continue
            if key not in result:
                result[key] = []

            result[key].append({
                "nombre": item.nombre,
                "desc": item.desc or ""
            })

        return result

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor", error=e)