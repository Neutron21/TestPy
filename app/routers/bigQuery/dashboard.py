from fastapi import APIRouter, HTTPException
from app.db import SessionDep
from app.routers.bigQuery.service_mysql import get_brokers_mysql, get_cotizacion_mysql, get_financieras_mysql, get_sedes_mysql, get_usuarios_mysql
from app.routers.bigQuery.service_bQ import (
    truncate_table,
    insert_rows
)

router = APIRouter(prefix="/sync/bigquery", tags=["BigQuery Sync"])

# @router.post("/brokers")  
def sync_brokers(session: SessionDep):
    brokers = get_brokers_mysql(session)

    if not brokers:
        raise HTTPException(400, "No hay brokers para sincronizar")
    truncate_table("analytics_konnect", "brokers")
    insert_rows("analytics_konnect", "brokers", brokers)

    # return { "status": "ok", "rows_synced": len(brokers) }
    return len(brokers) 

# @router.post("/cotizacion")
def sync_cotizacion(session: SessionDep):
    cotizacion = get_cotizacion_mysql(session)

    if not cotizacion:
        raise HTTPException(400, "No hay cotizacion para sincronizar")
    truncate_table("analytics_konnect", "cotizacion")
    insert_rows("analytics_konnect", "cotizacion", cotizacion)

    # return { "status": "ok", "rows_synced": len(cotizacion) }
    return len(cotizacion) 

# @router.post("/financieras")
def sync_financieras(session: SessionDep):
    financieras = get_financieras_mysql(session)

    if not financieras:
        raise HTTPException(400, "No hay financieras para sincronizar")
    truncate_table("analytics_konnect", "financieras")
    insert_rows("analytics_konnect", "financieras", financieras)

    # return { "status": "ok", "rows_synced": len(financieras) }
    return len(financieras) 

# @router.post("/sedes")
def sync_sedes(session: SessionDep):
    sedes = get_sedes_mysql(session)

    if not sedes:
        raise HTTPException(400, "No hay sedes para sincronizar")
    truncate_table("analytics_konnect", "sedes")
    insert_rows("analytics_konnect", "sedes", sedes)

    # return {"status": "ok", "rows_synced": len(sedes)}
    return len(sedes) 

# @router.post("/usuarios")
def sync_usuarios(session: SessionDep):
    usuarios = get_usuarios_mysql(session)

    if not usuarios:
        raise HTTPException(400, "No hay usuarios para sincronizar")
    truncate_table("analytics_konnect", "usuarios")
    insert_rows("analytics_konnect", "usuarios", usuarios)

    # return {"status": "ok", "rows_synced": len(usuarios)}
    return len(usuarios) 