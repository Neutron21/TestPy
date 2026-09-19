from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlmodel import select
from app.db import SessionDep
from app.models import CalculoComisiones, ResponsePagos, Cotizacion
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

@router.get("/pagos/comisiones")
async def obtener_calculo_comisiones_vigentes(session: SessionDep):
    query = text("""
        SELECT
            cc.id,
            cc.id_cotizacion AS folio,
            c.nombre AS cliente,
            cc.id_financiera,
            f.nombre AS financiera,
            cc.id_producto,
            p.nombre AS producto,
            cat.id AS id_categoria,
            cat.nombre AS linea,
            cc.id_usuario,
            u.nombre AS usuario,
            b.nombre AS broker,
            cc.monto_credito,
            cc.membresia_broker,
            cc.porcentaje_pago_konnect,
            cc.pago_konnect,
            cc.iva_pago_konnect,
            cc.total_pago_konnect,
            cc.porcentaje_pago_broker,
            cc.pago_broker,
            cc.iva_pago_broker,
            cc.total_pago_broker,
            cc.ganancia_konnect,
            cc.iva_ganancia_konnect,
            cc.total_ganancia_konnect,
            cc.regla_aplicada,
            cc.fecha_calculo,
            cc.es_vigente,
            cc.version,
            ur.nombre AS recalculado_por,
            cc.motivo_recalculo
        FROM calculo_comisiones cc
        INNER JOIN financieras f
            ON f.id = cc.id_financiera
        INNER JOIN productos p
            ON p.id = cc.id_producto
        INNER JOIN categorias cat
            ON p.id = cat.id
        INNER JOIN usuarios u
            ON u.id = cc.id_usuario
        LEFT JOIN usuarios ur
            ON ur.id = cc.recalculado_por
        INNER JOIN cotizacion c
            ON c.id_cotizacion = cc.id_cotizacion
        INNER JOIN brokers b
            ON c.broker = b.id
        WHERE cc.es_vigente = 1
    """)

    return [dict(row) for row in session.execute(query).mappings().all()]



@router.get("/pagos/calculo-comisiones-por-id/{id}", response_model=CalculoComisiones)
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