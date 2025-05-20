from itertools import product
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import ProductoFormatoTipoPersona, Productos, ProductosDTO, ProductosTipoPersonaDTO

router = APIRouter(tags=["Productos"])

@router.post("/producto", response_model=Productos) 
async def create_producto(producto_data: ProductosDTO, session: SessionDep):
    product = Productos.model_validate(producto_data.model_dump())  
    session.add(product)  
    session.commit() 
    session.refresh(product) 
    return product  

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

@router.get("/productos/tipoPersona/{financiera_id}", response_model=list[ProductosTipoPersonaDTO])
async def get_producto_by_financiera(financiera_id: int, session: SessionDep):
    query = select(Productos).where(Productos.institucion_id == financiera_id)
    productos_db = session.exec(query).all()

    productos_con_tipo_persona = []

    for producto in productos_db:  # Obtener tipos de persona por producto
       
        tipos = session.exec(
            select(ProductoFormatoTipoPersona.tipo_persona)
            .where(ProductoFormatoTipoPersona.producto_id == producto.id)
            .distinct()
        ).all()

        # Crear objeto del DTO con la info combinada
        dto = ProductosTipoPersonaDTO(
            id=producto.id,
            nombre=producto.nombre,
            checklist=producto.checklist,
            ch_viabilidad=producto.ch_viabilidad,
            institucion_id=producto.institucion_id,
            tipo_persona=tipos
        )

        productos_con_tipo_persona.append(dto)

    return productos_con_tipo_persona