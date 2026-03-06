

from app.models import Pagos


FINANCIERAS = {
    1: "KONFIO",
    10: "FINSUS",
    32: "CLARA",
    34: "FLUXO",
}
# Konfio
def porMontoProducto(id_if: int, id_producto: int, id_membresia: int, pagos: list[Pagos], monto):
    
    
    return f"Calular pagos de {FINANCIERAS.get(id_if)} IF: {id_if}"
# Finsus
def porCreditosColocados(id_if: int, id_producto: int, id_membresia: int, pagos: list[Pagos], monto):
    
    
    return f"Calular pagos de {FINANCIERAS.get(id_if)} IF: {id_if}"