from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Cotizacion, CotizacionDTO

router = APIRouter(tags=["Cotizacion"])


@router.get("/cotizacion/{id_cotizacion}" , response_model=Cotizacion)
async def get_cotizacion_by_id(id_cotizacion: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cotizacion = session.exec(query).first()
    if not cotizacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe la Cotización")
    return  cotizacion

@router.get("/cotizaciones/{id_usuario}", response_model=list[Cotizacion])
async def obtener_cotizaciones(id_usuario: str, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_usuario == id_usuario)
    cotizaciones = session.exec(query).all()
    
    return cotizaciones
@router.get("/cotizaciones/estatus/{estatus}", response_model=List[Cotizacion])
async def get_cotizaciones_by_estatus(estatus: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.estatus == estatus)
    cotizaciones = session.exec(query).all()
    if not cotizaciones:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existen Cotizaciones con ese estatus")
    return cotizaciones

@router.get("/cotizacion/nombre/{nombre}", response_model=List[Cotizacion])
async def get_cotizacion_by_nombre(nombre: str, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.nombre == nombre)
    cotizaciones = session.exec(query).all()
    if not cotizaciones:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron cotizaciones con ese nombre")
    return cotizaciones

@router.get("/cotizacion/rfc/{rfc}", response_model=List[Cotizacion])
async def get_cotizacion_by_rfc(rfc: str, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.rfc == rfc)
    cotizaciones = session.exec(query).all()
    if not cotizaciones:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron cotizaciones con ese RFC")
    return cotizaciones

@router.get("/cotizacion/folio/{folio}", response_model=List[Cotizacion])
async def get_cotizacion_by_folio(folio: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_cotizacion == folio)
    cotizaciones = session.exec(query).all()
    if not cotizaciones:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron cotizaciones con ese folio")
    return cotizaciones
@router.get("/cotizacion/folio/{folio}", response_model=List[Cotizacion])
async def get_cotizacion_by_folio(folio: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_cotizacion == folio)
    cotizaciones = session.exec(query).all()
    if not cotizaciones:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron cotizaciones con ese folio")
    return cotizaciones


@router.post("/cotizacion", response_model=Cotizacion) 
async def create_cotizacion(usuario_data: CotizacionDTO, session: SessionDep):
    cotizacion = Cotizacion.model_validate(usuario_data.model_dump())  
    session.add(cotizacion)  
    session.commit() 
    session.refresh(cotizacion) 
    return cotizacion  