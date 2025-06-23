from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Formatos, Producto_formato, ProductoFormatoTipoPersona

router = APIRouter(tags=["Formatos_Prodcutos"])


@router.get("/Producto_formato/{producto_id}", response_model=list[str])
async def formatos_financiera_OLD(producto_id: int, session: SessionDep):
    query = select(Formatos.nombre).join(Producto_formato, Producto_formato.formato_id == Formatos.id).where(Producto_formato.producto_id == producto_id)
    result = session.exec(query).all()
    # if not result:
        # raise HTTPException(status_code=404, detail="No se encontraron formatos para este producto")
    return result

@router.get("/formato_producto_persona", response_model=list[str])
async def formato_producto_persona(session: SessionDep, producto_id: int = Query(None), tipoPersona: str = Query(None)):
    
    if producto_id is None or tipoPersona is None:
        raise HTTPException(status_code=400, detail="Debe proporcionar producto_id y tipoPersona")
    
    query = select(Formatos.nombre).join(
        ProductoFormatoTipoPersona, ProductoFormatoTipoPersona.formato_id == Formatos.id
        ).where((ProductoFormatoTipoPersona.producto_id == producto_id) & (ProductoFormatoTipoPersona.tipo_persona == tipoPersona))
    result = session.exec(query).all()
    
    return result