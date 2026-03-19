from sqlmodel import func, select

from app.routers.pagos.model.baseFinanciera import BaseFinanciera, to_decimal_7_5
from app.models import Cotizacion, Pagos, ResponsePagos, Usuarios, Productos
from app.routers.pagos.model.baseFinanciera import MEMBRESIAS, FINANCIERAS

proceso_pago = 11

class FinsusCalculator(BaseFinanciera):

    def bussinesRules(self):

        id_user = self.cotizacion.id_user

        query_creditos = select(func.count()).select_from(Cotizacion).where(
            (Cotizacion.id_financiera == self.cotizacion.id_financiera) &
            (Cotizacion.id_user == id_user) &
            (Cotizacion.estatus == proceso_pago)
        )

        creditos_ant = self.session.exec(query_creditos).first()

        query_pagos = select(Pagos).where(Pagos.id_financiera == self.cotizacion.id_financiera)
        self.pagos_result = self.session.exec(query_pagos).all()

        query_user = select(Usuarios).where(Usuarios.id == self.cotizacion.id_user)
        self.user_result = self.session.exec(query_user).first()
        self.id_membresia = self.user_result.membresia

        query_producto = select(Productos.nombre).where(Productos.id == self.cotizacion.producto)
        self.producto_nombre = self.session.exec(query_producto).first()

        if creditos_ant == 0:
            self.regla = 1
            print("Primer credito 70%")
        elif creditos_ant == 1:
            self.regla = 2
            print("Segundo credito 40%")
        elif creditos_ant >= 2:
            self.regla = 3
            print("Tercer credito 20%")


    def calculate(self):

        self.bussinesRules()
        t_pago = next((p for p in self.pagos_result if p.m_min == self.regla), "None")
        print(f"ROW PAGO: {t_pago}")
        com_apertura = self.cotizacion.monto * t_pago.c_apertura
        print(f"com_apertura: {t_pago.c_apertura}% de {self.cotizacion.monto} -> {com_apertura}")
        calc_pago_konnect = t_pago.pago_a_konnect * com_apertura
        print(f"Pago Konnect: {calc_pago_konnect}, {t_pago.pago_a_konnect} de {com_apertura}")
    
        match self.id_membresia:
            case 1:
                comision_broker = t_pago.c_plata * calc_pago_konnect
            case 2:
                comision_broker = t_pago.c_oro * calc_pago_konnect
            case 3:
                comision_broker = t_pago.c_platino * calc_pago_konnect
            case 4:
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
            pago_a_konnect=to_decimal_7_5(calc_pago_konnect),
            ganancia_broker=to_decimal_7_5(comision_broker),
            ganancia_konnect=to_decimal_7_5(gan_konn)
        )     