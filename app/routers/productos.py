from itertools import product
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Tp_producto_checklist, Productos, ProductosDTO, ProductosTipoPersonaDTO
from sqlmodel import select


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
    query = select(Productos).where(Productos.institucion_id == financiera_id).order_by(Productos.nombre)
    productos_db = session.exec(query).all()

    productos_con_tipo_persona = []

    for producto in productos_db:  # Obtener tipos de persona por producto
       
        tipos = session.exec(
            select(Tp_producto_checklist.tipo_persona)
            .where(Tp_producto_checklist.producto_id == producto.id)
            .distinct()
        ).all()

        # Crear objeto del DTO con la info combinada
        dto = ProductosTipoPersonaDTO(
            id=producto.id,
            nombre=producto.nombre,
            checklist=producto.checklist,
            ch_viabilidad=producto.ch_viabilidad,
            institucion_id=producto.institucion_id,
            tipo_persona=tipos,
            id_categoria=producto.id_categoria,
            id_subCategoria=producto.id_subCategoria
        )

        productos_con_tipo_persona.append(dto)

    return productos_con_tipo_persona

@router.get("/producto/{producto_id}/plazos")
async def obtener_plazos(producto_id: int, session: SessionDep):

    producto = session.get(Productos, producto_id)

    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    if not producto.plazo:
        return {"plazos": []}

    raw_plazos = producto.plazo.split(",")
    print(raw_plazos)
   

    return {"plazos": raw_plazos}
@router.get("/producto/{producto_id}/nombre")
def get_producto_nombre(producto_id: int, session: SessionDep):

    stmt = select(Productos.nombre).where(Productos.id == producto_id)
    nombre = session.exec(stmt).first()

    if not nombre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    return {"nombre": nombre}


