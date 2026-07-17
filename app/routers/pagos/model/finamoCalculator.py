from sqlmodel import func, select

from app.routers.pagos.model.baseFinanciera import BaseFinanciera, status_pagado, to_decimal_7_5, show_percent, calc_IVA
from app.models import Cotizacion, Pagos, ResponsePagos, Usuarios, Productos
from app.routers.pagos.model.baseFinanciera import MEMBRESIAS, FINANCIERAS


class FinamoCalculator(BaseFinanciera):

    def bussinesRules(self):
        # Regla general aplica a todos los productos de Finamo
        query_pagos = select(Pagos).where(Pagos.id_financiera == self.cotizacion.id_financiera)
        self.pagos_result = self.session.exec(query_pagos).all()

        query_user = select(Usuarios).where(Usuarios.id == self.cotizacion.id_user)
        self.user_result = self.session.exec(query_user).first()
        self.id_membresia = self.user_result.membresia

        query_producto = select(Productos.nombre).where(Productos.id == self.cotizacion.producto)
        self.producto_nombre = self.session.exec(query_producto).first()


    def calculate(self):

        self.bussinesRules()
        print(f"Calculando {FINANCIERAS.get(self.cotizacion.id_financiera)} por monto de producto")
        t_pago = next((p for p in self.pagos_result), "None")
        print(f"t_pago: {t_pago}")
        com_apertura = self.cotizacion.monto * t_pago.c_apertura
        print(f"com_apertura: {t_pago.c_apertura}% de {self.cotizacion.monto} -> {com_apertura}")
        calc_pago_konnect = t_pago.pago_a_konnect * com_apertura
        print(f"Pago Konnect: {calc_pago_konnect}, {t_pago.pago_a_konnect} de {com_apertura}")
    
        match self.id_membresia:
            case 1:
                porcentaje_broker = t_pago.c_plata
                comision_broker = t_pago.c_plata * calc_pago_konnect
            case 2:
                porcentaje_broker = t_pago.c_oro
                comision_broker = t_pago.c_oro * calc_pago_konnect
            case 3:
                porcentaje_broker = t_pago.c_platino
                comision_broker = t_pago.c_platino * calc_pago_konnect
            case 4:
                porcentaje_broker = t_pago.c_diamante
                comision_broker = t_pago.c_diamante * calc_pago_konnect

        print(f"Membreisa Broker: {MEMBRESIAS.get(self.id_membresia)}")
        print(f"Comision Broker: {comision_broker}")
        gan_konn = calc_pago_konnect - comision_broker
        print(f"Ganancia Konnect: {gan_konn}")

        return ResponsePagos(
            id_cotizacion=self.cotizacion.id_cotizacion,
            id_financiera=self.cotizacion.id_financiera,
            financiera=FINANCIERAS.get(self.cotizacion.id_financiera),
            regla=t_pago.regla,
            id_producto=self.cotizacion.producto,
            producto=self.producto_nombre,
            membresia_broker=MEMBRESIAS.get(self.id_membresia),
            nombre_usuario=self.user_result.nombre,
            monto_credito=self.cotizacion.monto,
            
            comision_apertura_porcentaje = show_percent(t_pago.c_apertura),
            comision_apertura_pesos = str(com_apertura),
            
            porcentaje_pago_a_konnect = show_percent(t_pago.pago_a_konnect),
            pago_a_konnect=to_decimal_7_5(calc_pago_konnect),
            iva_pago_a_konnect = calc_IVA(calc_pago_konnect),
            total_pago_a_konnect = calc_pago_konnect + calc_IVA(calc_pago_konnect),
            
            porcentaje_pago_broker = show_percent(porcentaje_broker),
            pago_broker=to_decimal_7_5(comision_broker),
            iva_pago_broker = calc_IVA(comision_broker),
            total_pago_broker = comision_broker + calc_IVA(comision_broker),
            
            ganancia_konnect=to_decimal_7_5(gan_konn),
            iva_ganancia_konnect = calc_IVA(gan_konn),
            total_ganancia_konnect = gan_konn + calc_IVA(gan_konn),
            
        )     