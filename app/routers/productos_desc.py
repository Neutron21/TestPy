from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.db import SessionDep
from app.models import Productos, ProductoParametros,ProductoResponse, ParametroResponse
from pydantic import BaseModel



router = APIRouter(
    tags=["Productos Detalle"]
)


@router.get("/producto_detalle/{id_producto}", response_model=ProductoResponse)
async def get_producto(id_producto: int, session: SessionDep):

    producto = session.get(Productos, id_producto)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    parametros_query = (
        select(ProductoParametros)
        .where(ProductoParametros.id_producto == id_producto)
        .order_by(ProductoParametros.orden)
    )

    parametros_db = session.exec(parametros_query).all()

    parametros = [
        ParametroResponse(
            param=p.param,
            value=p.value,
            orden=p.orden
        )
        for p in parametros_db
    ]

    return ProductoResponse(
    id=producto.id,
    nombre=producto.nombre,
    parametros=parametros
)

@router.get("/producto_detalle_v2/{id_producto}", response_model=list[ProductoParametros])
async def get_producto_v2(id_producto: int, session: SessionDep):

    producto = session.get(Productos, id_producto)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    parametros_query = (
        select(ProductoParametros)
        .where(ProductoParametros.id_producto == id_producto)
        .order_by(ProductoParametros.orden)
    )
    parametros_db = session.exec(parametros_query).all()
    return parametros_db