from decimal import Decimal

from fastapi import HTTPException
from sqlmodel import select
from app.routers.pagos.model.baseFinanciera import FINANCIERAS, MEMBRESIAS, BaseFinanciera, to_decimal_7_5, show_percent, calc_IVA
from app.models import Cotizacion, Pagos, Productos, ResponsePagos, Usuarios


class KonfioCalculator(BaseFinanciera):

    def bussinesRules(self):

        monto = self.cotizacion.monto

        if self.cotizacion.producto == 16:
            query_pagos = select(Pagos).where(
                (Pagos.id_financiera == self.cotizacion.id_financiera) &
                (Pagos.id_producto == self.cotizacion.producto) &  
                (Pagos.m_min <= monto) &
                (Pagos.m_max >= monto)
                )
        if self.cotizacion.producto == 17:
            query_pagos = select(Pagos).where(
                (Pagos.id_financiera == self.cotizacion.id_financiera) &
                (Pagos.id_producto == self.cotizacion.producto) &
                (Pagos.notas == self.cotizacion.tipo_persona) &
                (Pagos.m_min <= monto) &
                (Pagos.m_max >= monto)
            )
        self.pagos_result = self.session.exec(query_pagos).first()
        if not self.pagos_result:
            raise HTTPException(status_code=404, detail="Regla de pago no encontrada")
        
        print(f"Pagos Result: {self.pagos_result}")

        query_user = select(Usuarios).where(Usuarios.id == self.cotizacion.id_user)
        self.user_result = self.session.exec(query_user).first()
        self.id_membresia = self.user_result.membresia

        query_producto = select(Productos.nombre).where(Productos.id == self.cotizacion.producto)
        self.producto_nombre = self.session.exec(query_producto).first()

    def calculate(self):
        self.bussinesRules()
        print(f"Calculando {FINANCIERAS.get(self.cotizacion.id_financiera)} por monto de producto")
        
        calc_pago_konnect=self.cotizacion.monto * self.pagos_result.pago_a_konnect
        
        match self.id_membresia:

            case 1:
                porcentaje_broker = self.pagos_result.c_plata
                comision_broker = self.pagos_result.c_plata * self.cotizacion.monto
            case 2:
                porcentaje_broker = self.pagos_result.c_oro
                comision_broker = self.pagos_result.c_oro * self.cotizacion.monto
            case 3:
                porcentaje_broker = self.pagos_result.c_platino
                comision_broker = self.pagos_result.c_platino * self.cotizacion.monto
            case 4:
                porcentaje_broker = self.pagos_result.c_diamante
                comision_broker = self.pagos_result.c_diamante * self.cotizacion.monto
        gan_konn = calc_pago_konnect - comision_broker


        return ResponsePagos(
            id_cotizacion=self.cotizacion.id_cotizacion,
            id_financiera=self.cotizacion.id_financiera,
            financiera=FINANCIERAS.get(self.cotizacion.id_financiera),
            regla=self.pagos_result.regla,
            id_producto=self.cotizacion.producto,
            producto=self.producto_nombre,
            membresia_broker=MEMBRESIAS.get(self.id_membresia),
            nombre_usuario=self.user_result.nombre,
            monto_credito=self.cotizacion.monto,

            comision_apertura_porcentaje = show_percent(self.pagos_result.c_apertura),
            comision_apertura_pesos = "0",

            porcentaje_pago_a_konnect = show_percent(self.pagos_result.pago_a_konnect),
            pago_a_konnect=to_decimal_7_5(calc_pago_konnect),
            iva_pago_a_konnect = calc_IVA(calc_pago_konnect),
            total_pago_a_konnect = calc_pago_konnect + calc_IVA(calc_pago_konnect),

            porcentaje_pago_broker = show_percent(porcentaje_broker),
            pago_broker=to_decimal_7_5(comision_broker),
            iva_pago_broker = calc_IVA(comision_broker),
            total_pago_broker = comision_broker + calc_IVA(comision_broker),

            ganancia_konnect=to_decimal_7_5(gan_konn),
            iva_ganancia_konnect = calc_IVA(gan_konn),
            total_ganancia_konnect = gan_konn + calc_IVA(gan_konn)
        )     