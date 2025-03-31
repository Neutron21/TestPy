from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Productos

router = APIRouter(tags=["Productos"])


@router.get("/productos", response_model=list[Productos])
async def list_productos(session: SessionDep):
    query = select(Productos)
    productos = session.exec(query).all()
    return productos

@router.get("/producto/{producto_id}", response_model=Productos)
async def get_producto_by_id(producto_id: int, session: SessionDep):
    producto_db = session.get(Productos, producto_id)
    if not producto_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe el Producto")
    return producto_db

@router.get("/productosByFin/{financiera_id}", response_model=list[Productos])
async def get_producto_by_financiera(financiera_id: int, session: SessionDep):
    query = select(Productos).where(Productos.institucion_id == financiera_id)
    productos_db = session.exec(query).all()
    print(productos_db) 
    return productos_db