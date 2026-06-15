from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal

from app.models import ResponsePagos

iva_value = Decimal("0.16")
status_pagado = 9
status_dispersion = 7

class BaseFinanciera(ABC):

    def __init__(self, cotizacion, session):
        self.cotizacion = cotizacion
        self.session = session
    
    @abstractmethod
    def bussinesRules(self) : # Aquí aplicas tu lógica
        pass

    @abstractmethod
    def calculate(self) -> ResponsePagos: # Aquí se calculan los pagos
        pass

def to_decimal_7_5(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)

def show_percent(value: Decimal) -> str:
    percent = value * 100
    return f"{str(percent.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP))} %"

def calc_IVA(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP) * iva_value

FINANCIERAS = {
    1: "KONFIO",
    10: "FINSUS",
    11: "FINBE ABC",
    20: "UNIFIN",
    22: "JEEVES",
    29: "FINKARGO",
    32: "CLARA",
    34: "FLUXO",
}
MEMBRESIAS = {
    1: "PLATA",
    2: "ORO",
    3: "PLATINO",
    4: "DIAMANTE",
}