from fastapi import HTTPException
from sqlmodel import func, select

from app.routers.pagos.mng_pagos import porCreditosColocados, porMontoProducto
from app.models import Cotizacion, Pagos, Usuarios
from app.db import SessionDep


CALCULOS = {
    1: porMontoProducto,
    10: porCreditosColocados,
    32: porMontoProducto,
    34: porMontoProducto,
}
no_product = [10]
proceso_pago = 11
def manager_func(id_cotizacion: int, session: SessionDep):

    print(f'Recibiendo cotizacion: {id_cotizacion}')

    query_cot = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cot_result = session.exec(query_cot).first()
    # print(f"Cotizacion: {cot_result}")

    if not cot_result:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    id_financiera = cot_result.id_financiera
    creditos_ant = 0

    if id_financiera in no_product: # FINSUS
        query_pagos = select(Pagos).where(Pagos.id_financiera == id_financiera)
        
        query_creditos_ant = select(func.count()).select_from(Cotizacion).where(
            (Cotizacion.id_financiera == id_financiera) &
            (Cotizacion.id_user == cot_result.id_user) &
            (Cotizacion.estatus == proceso_pago)
        )
        creditos_ant = session.exec(query_creditos_ant).first()
    else :
        query_pagos = select(Pagos).where(
            (Pagos.id_financiera == id_financiera) & 
            (Pagos.id_producto == cot_result.producto))
        
    pagos_result = session.exec(query_pagos).all()

    # print(f"Pagos: {pagos_result}")
    
    query_user = select(Usuarios).where(Usuarios.id == cot_result.id_user)
    user_result = session.exec(query_user).first()
    membresia = user_result.membresia

    print(f"User: {user_result}")
    funcion = CALCULOS.get(id_financiera)

    if not funcion:
        raise HTTPException(status_code=406, detail="Institución no soportada")
    return funcion(id_financiera, cot_result.producto, membresia, pagos_result, cot_result.monto, creditos_ant)