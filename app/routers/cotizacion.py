from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status, Path
from sqlmodel import select, text
from app.db import SessionDep
from app.models import Cotizacion, CotizacionDTO, EstatusUpdate

router = APIRouter(tags=["Cotizacion"])

@router.get("/cotizacion/{id_cotizacion}" , response_model=Cotizacion)
async def get_cotizacion_by_id(id_cotizacion: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cotizacion = session.exec(query).first()
    if not cotizacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe la Cotización")
    return  cotizacion

@router.get("/cotizaciones", response_model=list[Cotizacion])
async def obtener_cotizaciones(
    session: SessionDep,
    id_usuario: Optional[str] = Query(None)):
    if not id_usuario:
        query = select(Cotizacion)
    else:    
        query = select(Cotizacion).where(Cotizacion.id_usuario == id_usuario)
    cotizaciones = session.exec(query).all()
    
    return cotizaciones

@router.get("/cotizacion/buscar/", response_model=List[Cotizacion])
async def buscador_cotizaciones(
    session: SessionDep,
    estatus: Optional[int] = Query(None),
    fin: Optional[int] = Query(None),
    folioUserRfc: Optional[str] = Query(None),
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    user: Optional[str] = Query(None),
    rol: Optional[str] = Query(None),
    ):
    rows = [] 
    
    if estatus is None and fin is None and not folioUserRfc and not fechaDesde and not fechaHasta:
        raise HTTPException(status_code=400, detail="Error: Campos incompletos.")

    
    query = "SELECT * FROM cotizacion WHERE 1=1"
    params = {}

    if rol != 'a' and user:
        query += " AND id_usuario = :user"
        params["user"] = user

    if fechaDesde and fechaHasta:
        query += " AND timestamp BETWEEN :fechaDesde AND :fechaHasta"
        params["fechaDesde"] = fechaDesde
        params["fechaHasta"] = fechaHasta + " 23:59:59"

    if estatus is not None:
        query += " AND estatus = :estatus"
        params["estatus"] = estatus

    if fin is not None:
        query += " AND id_financiera = :fin"
        params["fin"] = fin

    if folioUserRfc:
        like = f"%{folioUserRfc}%"
        if rol == 'a':
            query += " AND (id_usuario LIKE :like OR nombre LIKE :like OR rfc LIKE :like OR id_cotizacion = :folioUserRfc)"
        else:
            query += " AND (nombre LIKE :like OR rfc LIKE :like OR id_cotizacion = :folioUserRfc)"
        params["like"] = like
        params["folioUserRfc"] = folioUserRfc

    print(f"QUERY: {query}")
    print(f"PARAMS: {params}")
    result = session.execute(text(query), params)

    rows = [Cotizacion(**row._mapping) for row in result]
    print(f"Total rows: {len(rows)} - contenido: {rows}")
   
    
    return rows

@router.post("/cotizacion", response_model=Cotizacion) 
async def create_cotizacion(usuario_data: CotizacionDTO, session: SessionDep):
    cotizacion = Cotizacion.model_validate(usuario_data.model_dump())  
    session.add(cotizacion)  
    session.commit() 
    session.refresh(cotizacion) 
    return cotizacion  

@router.patch("/cotizacion/status_udpate", response_model=Cotizacion)
async def update_estatus_cotizacion(
    estatus_data: EstatusUpdate, session: SessionDep,):

    cotizacion = session.get(Cotizacion, estatus_data.id_cotizacion)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    cotizacion.estatus = estatus_data.estatus
    session.add(cotizacion)
    session.commit()
    session.refresh(cotizacion)
    
    return cotizacion
