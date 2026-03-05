from fastapi import HTTPException




# FINANCIERAS = {
#     1: konfio.calcular_pago,
#     10: finsus.calcular_pago,
#     32: clara.calcular_pago,
#     34: fluxo.calcular_pago,
# }

def manager_func(id_financiera: int):

    print(f'Recibiendo idFinanciera: {id_financiera}')
    
    # funcion = FINANCIERAS.get(id_financiera)

    # if not funcion:
    #     raise HTTPException(status_code=406, detail="Institución no soportada")
    # return funcion()