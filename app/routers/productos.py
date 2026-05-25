from itertools import product
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import ProductoParametros, ProductoResponse, Tp_producto_checklist, Productos, ProductosDTO, ProductosTipoPersonaDTO



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

@router.get("/producto_detalle/{id_producto}", response_model=ProductoResponse)
async def get_producto(id_producto: int, session: SessionDep):

    producto = session.get(Productos, id_producto)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    parametros = session.exec(
        select(ProductoParametros)
        .where(ProductoParametros.id_producto == id_producto)
        .order_by(ProductoParametros.orden)
    ).all()

    return ProductoResponse(
        id=producto.id,
        nombre=producto.nombre,
        parametros=parametros 
    )


@router.get("/productos/tipoPersona/{financiera_id}", response_model=list[ProductosTipoPersonaDTO])
async def get_producto_by_financiera(financiera_id: int, session: SessionDep):
    query = select(Productos).where((Productos.institucion_id == financiera_id) & (Productos.visible == True)).order_by(Productos.nombre)
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

