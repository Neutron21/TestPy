from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.db import SessionDep
from app.models import CalculoComisiones, ResponsePagos
from app.routers.pagos.service_pagos import manager_func, manager_func_finkargo_custom


router = APIRouter(tags=["Pagos"])

@router.get("/pagos", response_model=ResponsePagos)
async def calular_comisiones(id_cotizacion: int, session: SessionDep):
    
    return manager_func(id_cotizacion, session)

@router.get("/pagos/finkargo-incremento", response_model=ResponsePagos)
async def calular_comisiones_finkargo_incremento(id_cotizacion: int, monto: int, session: SessionDep):
    """
    Calcula comisiones de Finkargo Incremento de linea con parámetros personalizados.
    
    Args:
        id_cotizacion: ID de la cotización (solo para validación de existencia)
        monto: Monto sobre el cual se harán los cálculos
        session: Sesión de base de datos
    
    El producto se usa automáticamente como  Finkargo Incremento de linea.
    """
    return manager_func_finkargo_custom(id_cotizacion, monto, 187, session)

@router.get("/pagos/finkargo-operativa", response_model=ResponsePagos)
async def calular_comisiones_finkargo_operativa(id_cotizacion: int, monto: int, session: SessionDep):
    """
    Calcula comisiones de Finkargo Operativa con parámetros personalizados.
    
    Args:
        id_cotizacion: ID de la cotización (solo para validación de existencia)
        monto: Monto sobre el cual se harán los cálculos
        session: Sesión de base de datos
    
    El producto se usa automáticamente como Finkargo Operativa.
    """ 
   
    return manager_func_finkargo_custom(id_cotizacion, monto, 186, session)

@router.get("/pagos/calculo-comisiones-vigentes", response_model=list[CalculoComisiones])
async def obtener_calculo_comisiones_vigentes(session: SessionDep):
    """
    Obtiene todos los registros donde es_vigente es igual a 1.
    """
    statement = select(CalculoComisiones).where(CalculoComisiones.es_vigente == 1)
    resultados = session.exec(statement).all()
    
    return resultados



@router.get("/pagos/calculo-comisiones-por-id-vigente/{id}", response_model=CalculoComisiones)
async def obtener_comision_por_id_siendo_vigente(id: int, session: SessionDep):
    """
    Busca un registro por su ID exacto y solo lo devuelve si su campo es_vigente es 1.
    """
    statement = (
        select(CalculoComisiones)
        .where(CalculoComisiones.id == id)
        .where(CalculoComisiones.es_vigente == 1)
    )
    registro = session.exec(statement).first()
    
    if not registro:
        raise HTTPException(
            status_code=404, 
            detail=f"El registro con ID {id} no tiene es_vigente = 1"
        )
        
    return registro