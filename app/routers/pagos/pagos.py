from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.db import SessionDep
from app.models import ResponsePagos
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
    
    El producto se usa automáticamente como 172 para Finkargo Incremento de linea.
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
    
    El producto se usa automáticamente como 173 para Finkargo Operativa.
    """ 
   
    return manager_func_finkargo_custom(id_cotizacion, monto, 186, session)