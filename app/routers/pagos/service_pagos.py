from fastapi import HTTPException
from sqlmodel import func, select

from app.models import Cotizacion, Pagos, Usuarios
from app.db import SessionDep
from app.routers.pagos.model.finsusCalculator import FinsusCalculator
from app.routers.pagos.model.konfioCalculator import  KonfioCalculator
from app.routers.pagos.model.fluxoCalculator import  FluxoCalculator
from app.routers.pagos.model.claraCalculator import  ClaraCalculator
    

CALCULOS = {
    1: KonfioCalculator, #✅
    10: FinsusCalculator, #✅
    32: ClaraCalculator,
    34: FluxoCalculator,
}

def manager_func(id_cotizacion: int, session: SessionDep):
    
    query_cot = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cot_result = session.exec(query_cot).first()

    if not cot_result:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    financiera_class = CALCULOS.get(cot_result.id_financiera)

    if not financiera_class:
        raise HTTPException(status_code=406, detail="Institución no soportada")

    financiera = financiera_class(cot_result, session)

    return financiera.calculate()