# 👀 se usa consulta cruda, para no depender de los modelos ya que las querys de fastapi regresan objetos en vez de dict
# 👀 ademas que de todos modos para enviar la info se tiene que mandar como diccionarios

from sqlalchemy import text
from datetime import datetime, date

# 👀 Mapeamos el objeto fecha o datetime para enviarlo como un string VALIDO
def serialize_row(row: dict, bool_fields=None):
    serialized = {}
    bool_fields = set(bool_fields or [])

    for key, value in row.items():
        if isinstance(value, (datetime, date)):
            serialized[key] = value.isoformat()
        elif key in bool_fields:
            if isinstance(value, bool):
                serialized[key] = value
            elif isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {"1", "true", "yes", "y"}:
                    serialized[key] = True
                elif normalized in {"0", "false", "no", "n", "null", "none"}:
                    serialized[key] = False
                else:
                    serialized[key] = bool(value)
            else:
                serialized[key] = bool(value)
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

def get_categorias_mysql(session):
    result = session.execute(
        text("""
            SELECT id, nombre
            FROM categorias
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

def get_estatus_tramites_mysql(session):
    result = session.execute(
        text("""
            SELECT id, name
            FROM estatus_tramites
        """)
    )
    return [dict(row._mapping) for row in result]


def get_membresias_mysql(session):
    result = session.execute(
        text("""
            SELECT id, nombre
            FROM membresias
        """)
    )
    return [dict(row._mapping) for row in result]


def get_track_status_mysql(session):
    result = session.execute(
        text("""
            SELECT id, id_cotizacion, id_status, fecha, id_usuario
            FROM track_status
        """)
    )
    return [serialize_row(dict(row._mapping)) for row in result]


def get_comentarios_mysql(session):
    result = session.execute(
        text("""
            SELECT id_comentario, id_cotizacion, id_usuario, comentarios, timestamp, visible
            FROM comentarios
        """)
    )
    return [serialize_row(dict(row._mapping), bool_fields={"visible"}) for row in result]


def get_financieras_mysql(session):
    result = session.execute(
        text("""
            SELECT id, nombre, tipo, fase
            FROM financieras
        """)
    )
    return [dict(row._mapping) for row in result]

def get_productos_mysql(session):
    result = session.execute(
        text("""
            SELECT id, nombre, institucion_id, id_categoria, id_subCategoria, plazo
            FROM productos
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

def get_subCategorias_mysql(session):
    result = session.execute(
        text("""
            SELECT id, id_categoria, nombre
            FROM subCategorias
        """)
    )
    return [dict(row._mapping) for row in result]

def get_usuarios_mysql(session):
    result = session.execute(
        text("""
            SELECT id, nombre, email, rol, rfc, id_broker, id_sede, membresia, celular, nivel, id_superior, id_financiera, created_at, comisiones, f_ultimo_pago
            FROM usuarios
        """)
    )
    return [serialize_row(dict(row._mapping)) for row in result]
    # return [dict(row._mapping) for row in result]