from sqlmodel import func, select
from typing import Optional

from app.routers.pagos.model.baseFinanciera import BaseFinanciera, status_pagado, to_decimal_7_5, show_percent, calc_IVA
from app.models import Cotizacion, Pagos, ResponsePagos, Usuarios, Productos
from app.routers.pagos.model.baseFinanciera import MEMBRESIAS, FINANCIERAS



class FinkargoCalculator(BaseFinanciera):

    def __init__(self, cotizacion, session, monto_override: Optional[int] = None, id_producto_override: Optional[int] = None):
        """
        Inicializa el calculador de Finkargo.
        
        Args:
            cotizacion: Objeto Cotizacion
            session: Sesión de base de datos
            monto_override: Monto personalizado para los cálculos (si es None, usa el de la cotización)
            id_producto_override: Producto personalizado para los cálculos (si es None, usa el de la cotización)
        """
        super().__init__(cotizacion, session)
        self.monto_override = monto_override
        self.id_producto_override = id_producto_override

    def bussinesRules(self):

        # Usar producto personalizado si se proporcionó, sino usar el de la cotización
        id_producto_a_usar = self.id_producto_override if self.id_producto_override is not None else self.cotizacion.producto
        
        query_pagos = select(Pagos).where(
            (Pagos.id_financiera == self.cotizacion.id_financiera) &
            (Pagos.id_producto == id_producto_a_usar)
            )
        self.pagos_result = self.session.exec(query_pagos).first()
        print(self.pagos_result)

        query_user = select(Usuarios).where(Usuarios.id == self.cotizacion.id_user)
        self.user_result = self.session.exec(query_user).first()
        self.id_membresia = self.user_result.membresia

        query_producto = select(Productos.nombre).where(Productos.id == id_producto_a_usar)
        self.producto_nombre = self.session.exec(query_producto).first()


    def calculate(self):

        self.bussinesRules()
        print(f"Calculando {FINANCIERAS.get(self.cotizacion.id_financiera)} por monto de producto")
        
        # Usar monto personalizado si se proporcionó, sino usar el de la cotización
        monto_a_usar = self.monto_override if self.monto_override is not None else self.cotizacion.monto
        
        t_pago = self.pagos_result
        print(f"Tipo de pago: {t_pago}")

        if t_pago.c_apertura > 0:
            com_apertura = monto_a_usar * t_pago.c_apertura
            print(f"com_apertura: {t_pago.c_apertura}% de {monto_a_usar} -> {com_apertura}")
        else:
            com_apertura = monto_a_usar # Se calcula sobre el monto total si no hay comisión de apertura

        calc_pago_konnect = t_pago.pago_a_konnect * com_apertura
        print(f"Pago Konnect: {calc_pago_konnect}, {t_pago.pago_a_konnect} de {com_apertura}")
            
        match self.id_membresia:
            case 1:
                porcentaje_broker = t_pago.c_plata
                comision_broker = t_pago.c_plata * com_apertura
            case 2:
                porcentaje_broker = t_pago.c_oro
                comision_broker = t_pago.c_oro * com_apertura
            case 3:
                porcentaje_broker = t_pago.c_platino
                comision_broker = t_pago.c_platino * com_apertura
            case 4:
                porcentaje_broker = t_pago.c_diamante
                comision_broker = t_pago.c_diamante * com_apertura

        print(f"Membreisa Broker: {MEMBRESIAS.get(self.id_membresia)}")
        print(f"Comision Broker: {comision_broker}")
        gan_konn = calc_pago_konnect - comision_broker
        print(f"Ganancia Konnect: {gan_konn}")

        # Usar producto personalizado si se proporcionó para mostrar en la respuesta
        id_producto_respuesta = self.id_producto_override if self.id_producto_override is not None else self.cotizacion.producto
        
        return ResponsePagos(
            id_cotizacion=self.cotizacion.id_cotizacion,
            id_financiera=self.cotizacion.id_financiera,
            financiera=FINANCIERAS.get(self.cotizacion.id_financiera),
            regla=t_pago.regla,
            id_producto=id_producto_respuesta,
            producto=self.producto_nombre,
            membresia_broker=MEMBRESIAS.get(self.id_membresia),
            nombre_usuario=self.user_result.nombre,
            monto_credito=monto_a_usar,
            
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
    