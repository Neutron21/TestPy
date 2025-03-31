from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Cotizacion

router = APIRouter(tags=["Cotizacion"])


@router.get("/Cotizacion/{id_cotizacion}" , response_model=list[Cotizacion])
async def Cotizacion(id_cotizacion: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cotizacion = session.exec(query)
    return  cotizacion

@router.get("/cotizaciones/{id_usuario}", response_model=list[Cotizacion])
async def obtener_cotizaciones(id_usuario: str, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_usuario == id_usuario)
    cotizaciones = session.exec(query).all()  # Se usa `.all()` para obtener la lista de resultados
    
    if not cotizaciones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontraron cotizaciones para el usuario {id_usuario}"
        )
    
    return cotizaciones