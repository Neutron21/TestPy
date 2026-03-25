from decimal import Decimal

from sqlmodel import select
from app.routers.pagos.model.baseFinanciera import FINANCIERAS, MEMBRESIAS, BaseFinanciera, to_decimal_7_5
from app.models import Cotizacion, Pagos, Productos, ResponsePagos, Usuarios


class FluxoCalculator(BaseFinanciera):

    def bussinesRules(self):

        monto = self.cotizacion.monto

        query_pagos = select(Pagos).where(
            (Pagos.id_financiera == self.cotizacion.id_financiera) &
            (Pagos.id_producto == self.cotizacion.producto)
            )
        self.pagos_result = self.session.exec(query_pagos).first()
        print(self.pagos_result)

        query_user = select(Usuarios).where(Usuarios.id == self.cotizacion.id_user)
        self.user_result = self.session.exec(query_user).first()
        self.id_membresia = self.user_result.membresia

        query_producto = select(Productos.nombre).where(Productos.id == self.cotizacion.producto)
        self.producto_nombre = self.session.exec(query_producto).first()

    def calculate(self):
        self.bussinesRules()
        print(f"Calculando {FINANCIERAS.get(self.cotizacion.id_financiera)} por monto de producto")

        comision_pa = self.pagos_result.c_apertura * self.cotizacion.monto
        calc_pago_konnect = self.pagos_result.pago_a_konnect * self.cotizacion.monto
        comision_broker=Decimal("200.0")
        gan_konn=Decimal("400.0")

        # aquí va tu query de pagos
        # aquí aplicas tu lógica

        return ResponsePagos(
            id_cotizacion=self.cotizacion.id_cotizacion,
            id_financiera=self.cotizacion.id_financiera,
            financiera=FINANCIERAS.get(self.cotizacion.id_financiera),
            regla="self.pagos_result.regla",
            id_producto=self.cotizacion.producto,
            producto=self.producto_nombre,
            membresia_broker=MEMBRESIAS.get(self.id_membresia),
            nombre_usuario=self.user_result.nombre,
            monto_credito=self.cotizacion.monto,
            pago_a_konnect=to_decimal_7_5(calc_pago_konnect),
            ganancia_broker=to_decimal_7_5(comision_broker),
            ganancia_konnect=to_decimal_7_5(gan_konn)
        )     