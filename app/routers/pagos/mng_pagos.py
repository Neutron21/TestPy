from app.models import Pagos


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
# Konfio
def porMontoProducto(id_if: int, id_producto: int, id_membresia: int, pagos: list[Pagos], monto):

    
    return f"Calular pagos de {FINANCIERAS.get(id_if)} IF: {id_if}"
# Finsus
def porCreditosColocados(id_if: int, id_producto: int, id_membresia: int, pagos: list[Pagos], monto, creditos_ant):
    print(creditos_ant)
    if creditos_ant == 0:
        regla = 1
        print("primer credito 70%")
    elif creditos_ant == 1:
        regla = 2
        print("segundo credito 40%")
    else:
        regla = 3
        print("tercer credito 20%")

    t_pago = next((p for p in pagos if p.m_min == regla), None)
    print(f"PAGO BUENO: {t_pago}")
    com_apertura = monto * t_pago.c_apertura
    print(f"com_apertura: {t_pago.c_apertura}% de {monto} -> {com_apertura}")
    calc_pago_konnect = t_pago.pago_a_konnect * com_apertura
    print(f"Pago Konnect: {calc_pago_konnect}, {t_pago.pago_a_konnect} de {com_apertura}")
   
    match id_membresia:
        case 1:
            comision_broker = t_pago.c_plata * calc_pago_konnect
        case 2:
            comision_broker = t_pago.c_oro * calc_pago_konnect
        case 3:
            comision_broker = t_pago.c_platino * calc_pago_konnect
        case 4:
            comision_broker = t_pago.c_diamante * calc_pago_konnect
    print(f"Membreisa Broker: {MEMBRESIAS.get(id_membresia)}")
    print(f"Comision Broker: {comision_broker}")
    print(f"Ganancia Konnect: {calc_pago_konnect - comision_broker}")

    return f"Calular pagos de {FINANCIERAS.get(id_if)} IF: {id_if}"