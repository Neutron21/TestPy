from decimal import Decimal

from sqlmodel import select
from app.routers.pagos.model.baseFinanciera import FINANCIERAS, MEMBRESIAS, BaseFinanciera, to_decimal_7_5
from app.models import Cotizacion, Pagos, Productos, ResponsePagos, Usuarios


class KonfioCalculator(BaseFinanciera):

    def bussinesRules(self):

        monto = self.cotizacion.monto

        query_pagos = select(Pagos).where(
            (Pagos.id_financiera == self.cotizacion.id_financiera) &
            (Pagos.id_producto == self.cotizacion.producto) &
            (Pagos.m_min <= monto) &
            (Pagos.m_max >= monto)
            )
        self.pagos_result = self.session.exec(query_pagos).first()
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
                comision_broker = self.pagos_result.c_plata * self.cotizacion.monto
            case 2:
                comision_broker = self.pagos_result.c_oro * self.cotizacion.monto
            case 3:
                comision_broker = self.pagos_result.c_platino * self.cotizacion.monto
            case 4:
                comision_broker = self.pagos_result.c_diamante * self.cotizacion.monto
        gan_konn = calc_pago_konnect - comision_broker

        # aquí va tu query de pagos
        # aquí aplicas tu lógica

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
            pago_a_konnect=to_decimal_7_5(calc_pago_konnect),
            ganancia_broker=to_decimal_7_5(comision_broker),
            ganancia_konnect=to_decimal_7_5(gan_konn)
        )     