from fastapi import HTTPException
from sqlmodel import select

from app.models import Cotizacion
from app.db import SessionDep
from app.routers.pagos.model.finsusCalculator import FinsusCalculator
from app.routers.pagos.model.konfioCalculator import  KonfioCalculator
from app.routers.pagos.model.fluxoCalculator import  FluxoCalculator
from app.routers.pagos.model.claraCalculator import  ClaraCalculator
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


def manager_func_finkargo_custom(id_cotizacion: int, monto: int, id_producto: int, session: SessionDep):
    """
    Calcula comisiones de Finkargo con monto y producto personalizados.
    Solo valida que la cotización existe, pero usa los parámetros del endpoint para los cálculos.
    
    Args:
        id_cotizacion: ID de cotización (solo para validación)
        monto: Monto sobre el cual se harán los cálculos
        id_producto: Producto para hacer los cálculos (ej: 172 para finkargo-incremento)
        session: Sesión de base de datos
    """
    # Validar que la cotización existe y es de Finkargo
    query_cot = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cot_result = session.exec(query_cot).first()

    if not cot_result:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    if cot_result.id_financiera != 29:
        raise HTTPException(status_code=406, detail="Esta función solo soporta Finkargo")
    
    # Usar el calculador de Finkargo con los parámetros personalizados
    # El constructor acepta monto_override e id_producto_override
    financiera = FinkargoCalculator(cot_result, session, monto_override=monto, id_producto_override=id_producto)
    
    return financiera.calculate()
