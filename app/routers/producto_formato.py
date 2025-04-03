from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Formatos, Producto_formato

router = APIRouter(tags=["Producto_formatos"])


@router.get("/Producto_formato/{producto_id}", response_model=list[str])
async def formatos_financiera(producto_id: int, session: SessionDep):
    query = select(Formatos.nombre).join(Producto_formato, Producto_formato.formato_id == Formatos.id).where(Producto_formato.producto_id == producto_id)
    result = session.exec(query).all()
    if not result:
        raise HTTPException(status_code=404, detail="No se encontraron formatos para este producto")
    return result

   