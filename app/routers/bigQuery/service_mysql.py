# 👀 se usa consulta cruda, para no depender de los modelos ya que las querys de fastapi regresan objetos en vez de dict
# 👀 ademas que de todos modos para enviar la info se tiene que mandar como diccionarios

from sqlalchemy import text
from datetime import datetime, date

# 👀 Mapeamos el objeto fecha o datetime para enviarlo como un string VALIDO
def serialize_row(row: dict):
    serialized = {}
    for key, value in row.items():
        if isinstance(value, (datetime, date)):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    return serialized

def get_brokers_mysql(session):
    result = session.execute(
        text("""
            SELECT id, nombre
            FROM brokers
        """)
    )
    return [dict(row._mapping) for row in result]

def get_cotizacion_mysql(session):
    result = session.execute(
        text("""
            SELECT id_cotizacion, id_usuario, id_financiera, producto, tipo_persona, nombre, rfc, plazo, edad, monto,
                    ingresos, estatus, timestamp, antiguedad_empresa, OpCliente, broker, sede, custom_prod, 
                    destinoCredito, id_user, fecha_pago
              FROM cotizacion
        """)
    )
    return [serialize_row(dict(row._mapping)) for row in result]

def get_financieras_mysql(session):
    result = session.execute(
        text("""
            SELECT id, nombre, tipo, fase
            FROM financieras
        """)
    )
    return [dict(row._mapping) for row in result]

def get_sedes_mysql(session):
    result = session.execute(
        text("""
            SELECT id, nombre
            FROM sedes
        """)
    )
    return [dict(row._mapping) for row in result]

def get_usuarios_mysql(session):
    result = session.execute(
        text("""
            SELECT id, nombre, email, rol, id_broker, id_sede, membresia, celular, nivel, id_superior, id_financiera
            FROM usuarios
        """)
    )
    return [dict(row._mapping) for row in result]