from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlmodel import select, desc

from app.models import Cotizacion, CalculoComisiones, ResponsePagos
from app.db import SessionDep
from app.routers.pagos.model.finsusCalculator import FinsusCalculator
from app.routers.pagos.model.konfioCalculator import KonfioCalculator
from app.routers.pagos.model.fluxoCalculator import FluxoCalculator
from app.routers.pagos.model.claraCalculator import ClaraCalculator
from app.routers.pagos.model.jeevesCalculator import JeevesCalculator
from app.routers.pagos.model.finbeAbcCalculator import FinbeAbcCalculator
from app.routers.pagos.model.finkargoCalculator import FinkargoCalculator
from app.routers.pagos.model.unifinCalculator import UnifinCalculator
from app.routers.pagos.model.afirmeCalculator import AfirmeCalculator
from app.routers.pagos.model.finamoCalculator import FinamoCalculator
    

CALCULOS = {
    1: KonfioCalculator, #✅ Pendinte TDCE
    10: FinsusCalculator, #✅
    11: FinbeAbcCalculator, #
    14: AfirmeCalculator, #
    20: UnifinCalculator, #✅
    22: JeevesCalculator, #✅
    24: FinamoCalculator, #
    29: FinkargoCalculator, #✅
    32: ClaraCalculator, #✅ Dispersados por mes
    34: FluxoCalculator, #✅ 
}

def guardar_registro_pagos(session, obj_res_pagos: ResponsePagos, id_user: int, motivo: str = "Cálculo de comisiones") -> ResponsePagos:
    id_cot = obj_res_pagos.id_cotizacion
    
    statement_vigente = select(CalculoComisiones).where(
        (CalculoComisiones.id_cotizacion == id_cot) & 
        (CalculoComisiones.es_vigente == 1)
    )
    registros_vigentes = session.exec(statement_vigente).all()
    for reg in registros_vigentes:
        reg.es_vigente = 0
        session.add(reg)

    statement_version = select(CalculoComisiones).where(
        CalculoComisiones.id_cotizacion == id_cot
    ).order_by(desc(CalculoComisiones.version))
    
    ultimo_calculo = session.exec(statement_version).first()
    nueva_version = (ultimo_calculo.version + 1) if (ultimo_calculo and ultimo_calculo.version is not None) else 1

    nuevo_calculo = CalculoComisiones(
        id_cotizacion=obj_res_pagos.id_cotizacion,
        version=nueva_version,
        id_financiera=obj_res_pagos.id_financiera,
        id_producto=obj_res_pagos.id_producto,
        id_usuario=id_user,
        membresia_broker=obj_res_pagos.membresia_broker,
        
        porcentaje_pago_konnect=obj_res_pagos.porcentaje_pago_a_konnect,
        pago_konnect=obj_res_pagos.pago_a_konnect,
        iva_pago_konnect=obj_res_pagos.iva_pago_a_konnect,
        total_pago_konnect=obj_res_pagos.total_pago_a_konnect,
        
        porcentaje_pago_broker=obj_res_pagos.porcentaje_pago_broker,
        pago_broker=obj_res_pagos.pago_broker,
        iva_pago_broker=obj_res_pagos.iva_pago_broker,
        total_pago_broker=obj_res_pagos.total_pago_broker,
        
        ganancia_konnect=obj_res_pagos.ganancia_konnect,
        iva_ganancia_konnect=obj_res_pagos.iva_ganancia_konnect,
        total_ganancia_konnect=obj_res_pagos.total_ganancia_konnect,
        
        regla_aplicada=obj_res_pagos.regla,
        fecha_calculo=datetime.now(ZoneInfo("America/Mexico_City")),
        es_vigente=1,
        motivo_recalculo=motivo if nueva_version > 1 else "Cálculo inicial"
    )

    session.add(nuevo_calculo)
    session.commit()
    session.refresh(nuevo_calculo)
    
    return obj_res_pagos


def manager_func(id_cotizacion: int, session: SessionDep):
    query_cot = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cot_result = session.exec(query_cot).first()

    if not cot_result:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    financiera_class = CALCULOS.get(cot_result.id_financiera)

    if not financiera_class:
        raise HTTPException(status_code=406, detail="Institución no soportada")

    financiera = financiera_class(cot_result, session)
    response_pagos = financiera.calculate()
    guardar_registro_pagos(session, response_pagos, id_user=cot_result.id_user)
    return response_pagos


def manager_func_finkargo_custom(id_cotizacion: int, monto: int, id_producto: int, session: SessionDep):
    query_cot = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cot_result = session.exec(query_cot).first()

    if not cot_result:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    if cot_result.id_financiera != 29:
        raise HTTPException(status_code=406, detail="Esta función solo soporta Finkargo")
    
    financiera = FinkargoCalculator(cot_result, session, monto_override=monto, id_producto_override=id_producto)
    response_pagos = financiera.calculate()

    return guardar_registro_pagos(session, response_pagos, id_user=cot_result.id_user, motivo="Recálculo personalizado Finkargo")