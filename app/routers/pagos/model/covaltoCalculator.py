from decimal import Decimal
from fastapi import HTTPException


class CovaltoCalculator:
    # Producto IDs
    PRODUCTO_CREDITO_SIMPLE_REVOLVENTE = 22
    PRODUCTO_FACTORAJE = 25

    # Mientras no exista un campo que distinga los dos factorajes,
    # el producto 25 se tratará como CXA por defecto.
    TIPO_FACTORAJE_DEFAULT = "CXA"

    # Rangos de montos y porcentajes pagados a Konnect.
    # Los límites superiores se incluyen en cada rango.
    REGLAS_MONTO = (
        {
            "min": Decimal("1000000"),
            "max": Decimal("6000000"),
            "pago_konnect": Decimal("0.50"),
            "indice": 0,
        },
        {
            "min": Decimal("6000000"),
            "max": Decimal("21000000"),
            "pago_konnect": Decimal("0.60"),
            "indice": 1,
        },
        {
            "min": Decimal("21000000"),
            "max": Decimal("51000000"),
            "pago_konnect": Decimal("0.70"),
            "indice": 2,
        },
        {
            "min": Decimal("51000000"),
            "max": Decimal("100000000"),
            "pago_konnect": Decimal("0.80"),
            "indice": 3,
        },
    )

    # Porcentajes de comisión de apertura por tipo de producto.
    COMISION_APERTURA = {
        "CREDITO_SIMPLE_REVOLVENTE": Decimal("0.035"),
        "CXA": Decimal("0.035"),
        "OPERATIVA": Decimal("0.015"),
    }

    MEMBRESIAS = {
        1: "PLATA",
        2: "ORO",
        3: "PLATINO",
        4: "DIAMANTE",
    }

    # Porcentajes de pago al broker por rango y membresía.
    # Orden de cada fila: Plata, Oro, Platino, Diamante.
    PORCENTAJES_BROKER = {
        "CREDITO_SIMPLE_REVOLVENTE": (
            (Decimal("0.25"), Decimal("0.30"),
             Decimal("0.35"), Decimal("0.40")),
            (Decimal("0.30"), Decimal("0.36"),
             Decimal("0.42"), Decimal("0.48")),
            (Decimal("0.35"), Decimal("0.42"),
             Decimal("0.5005"), Decimal("0.5502")),
            (Decimal("0.40"), Decimal("0.48"),
             Decimal("0.5504"), Decimal("0.64")),
        ),
        "CXA": (
            (Decimal("0.25"), Decimal("0.30"),
             Decimal("0.35"), Decimal("0.40")),
            (Decimal("0.30"), Decimal("0.36"),
             Decimal("0.42"), Decimal("0.48")),
            (Decimal("0.35"), Decimal("0.42"),
             Decimal("0.5005"), Decimal("0.5502")),
            (Decimal("0.40"), Decimal("0.48"),
             Decimal("0.5504"), Decimal("0.64")),
        ),
        "OPERATIVA": (
            (Decimal("0.25"), Decimal("0.30"),
             Decimal("0.35"), Decimal("0.40")),
            (Decimal("0.30"), Decimal("0.36"),
             Decimal("0.42"), Decimal("0.48")),
            (Decimal("0.35"), Decimal("0.42"),
             Decimal("0.5005"), Decimal("0.5502")),
            (Decimal("0.40"), Decimal("0.48"),
             Decimal("0.5504"), Decimal("0.64")),
        ),
    }

    # Porcentajes de ganancia, orden: Plata, Oro, Platino, Diamante.
    PORCENTAJES_GANANCIA_BROKER = (
        (Decimal("0.25"), Decimal("0.20"),
         Decimal("0.15"), Decimal("0.10")),
        (Decimal("0.30"), Decimal("0.24"),
         Decimal("0.18"), Decimal("0.12")),
        (Decimal("0.35"), Decimal("0.28"),
         Decimal("0.1995"), Decimal("0.1498")),
        (Decimal("0.40"), Decimal("0.32"),
         Decimal("0.2496"), Decimal("0.16")),
    )

    # Ganancia de Konnect por rango.
    # None significa que no se debe calcular ganancia de Konnect.
    PORCENTAJES_GANANCIA_KONNECT = {
        "CREDITO_SIMPLE_REVOLVENTE": (
            Decimal("-0.10"),
            Decimal("-0.12"),
            Decimal("-0.1498"),
            Decimal("-0.16"),
        ),
        "CXA": (
            Decimal("-0.10"),
            Decimal("-0.12"),
            Decimal("-0.1498"),
            Decimal("-0.16"),
        ),
        "OPERATIVA": (None, None, None, None),
    }

    @classmethod
    def obtener_rango(cls, monto: Decimal) -> dict:
        """
        Selecciona el rango de monto.
        Los límites compartidos se asignan al rango inferior:
        6 MDP -> 50%, 21 MDP -> 60%, 51 MDP -> 70%.
        """
        monto = Decimal(str(monto))

        for indice, regla in enumerate(cls.REGLAS_MONTO):
            minimo = regla["min"]
            maximo = regla["max"]

            if indice == 0:
                cumple_minimo = monto >= minimo
            else:
                cumple_minimo = monto > minimo

            if cumple_minimo and monto <= maximo:
                return regla

        raise ValueError(
            "Covalto solo admite montos desde $1,000,000 "
            "hasta $100,000,000."
        )

    @classmethod
    def obtener_tipo_operacion(cls, producto_id: int, tipo_factoraje=None):
        """
        Devuelve la clave usada para consultar las reglas.
        El tipo de factoraje debe venir de un dato externo si se
        necesita distinguir CXA de Procesamiento para el mismo ID 25.
        """
        if producto_id == cls.PRODUCTO_CREDITO_SIMPLE_REVOLVENTE:
            return "CREDITO_SIMPLE_REVOLVENTE"

        if producto_id == cls.PRODUCTO_FACTORAJE:
            tipo = (
                tipo_factoraje or cls.TIPO_FACTORAJE_DEFAULT
            ).strip().upper()

            if tipo in ("CXA", "FACTORAJE CXA"):
                return "CXA"

            if tipo in (
                "OPERATIVA",
                "PROCESAMIENTO",
                "FACTORAJE POR OPERATIVA (PROCESAMIENTO)",
            ):
                return "OPERATIVA"

            raise ValueError(
                "Tipo de factoraje no reconocido. "
                "Usa 'CXA' u 'OPERATIVA'."
            )

        raise ValueError(
            f"El producto {producto_id} no está configurado para Covalto."
        )

    @classmethod
    def obtener_porcentajes(
        cls,
        monto: Decimal,
        producto_id: int,
        membresia_id: int,
        tipo_factoraje=None,
    ) -> dict:
        """
        Obtiene las reglas aplicables a una cotización.
        No calcula ni modifica el modelo ResponsePagos.
        """
        rango = cls.obtener_rango(monto)

        tipo_operacion = cls.obtener_tipo_operacion(
            producto_id,
            tipo_factoraje,
        )

        if membresia_id not in cls.MEMBRESIAS:
            raise ValueError(
                f"La membresía {membresia_id} no es válida."
            )

        indice_rango = rango["indice"]
        indice_membresia = membresia_id - 1

        comision_apertura = cls.COMISION_APERTURA[tipo_operacion]

        porcentaje_broker = cls.PORCENTAJES_BROKER[
            tipo_operacion
        ][indice_rango][indice_membresia]

        porcentaje_ganancia_broker = (
            cls.PORCENTAJES_GANANCIA_BROKER[
                indice_rango
            ][indice_membresia]
        )

        porcentaje_ganancia_konnect = (
            cls.PORCENTAJES_GANANCIA_KONNECT[
                tipo_operacion
            ][indice_rango]
        )

        return {
            "tipo_operacion": tipo_operacion,
            "rango": indice_rango + 1,
            "comision_apertura": comision_apertura,
            "pago_konnect": rango["pago_konnect"],
            "porcentaje_broker": porcentaje_broker,
            "ganancia_broker": porcentaje_ganancia_broker,
            "ganancia_konnect": porcentaje_ganancia_konnect,
        }


