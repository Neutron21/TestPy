from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal

from app.models import ResponsePagos

class BaseFinanciera(ABC):

    def __init__(self, cotizacion, session):
        self.cotizacion = cotizacion
        self.session = session

    @abstractmethod
    def bussinesRules(self) :
        pass

    @abstractmethod
    def calculate(self) -> ResponsePagos:
        pass
def to_decimal_7_5(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)

FINANCIERAS = {
    1: "KONFIO",
    10: "FINSUS",
    32: "CLARA",
    34: "FLUXO",
}
MEMBRESIAS = {
    1: "PLATA",
    2: "ORO",
    3: "PLATINO",
    4: "DIAMANTE",
}