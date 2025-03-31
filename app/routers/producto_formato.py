from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Producto_formato

router = APIRouter(tags=["Producto_formatos"])


@router.get("/Producto_formato/{producto_id}" , response_model=list[Producto_formato])
async def formatos_financiera(producto_id: int, session: SessionDep):
    query = select(Producto_formato).where(Producto_formato.producto_id == producto_id)
    formatos = session.exec(query)
    return formatos
   