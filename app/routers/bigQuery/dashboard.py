from fastapi import APIRouter, HTTPException
from app.db import SessionDep
from app.routers.bigQuery.service_mysql import (get_brokers_mysql, get_cotizacion_mysql, get_estatus_tramites_mysql, 
                                                get_financieras_mysql, get_productos_mysql, get_sedes_mysql, get_usuarios_mysql,
                                                get_categorias_mysql, get_subCategorias_mysql)
from app.routers.bigQuery.service_bQ import (
    ensure_table,
    truncate_table,
    insert_rows,
    SCHEMAS
)

router = APIRouter(prefix="/sync/bigquery", tags=["BigQuery Sync"])

# @router.post("/brokers")  
def sync_brokers(session: SessionDep):
    brokers = get_brokers_mysql(session)

    if not brokers:
        raise HTTPException(400, "No hay brokers para sincronizar")
    ensure_table("analytics_konnect", "brokers", SCHEMAS["brokers"])
    truncate_table("analytics_konnect", "brokers")
    insert_rows("analytics_konnect", "brokers", brokers)

    # return { "status": "ok", "rows_synced": len(brokers) }
    return len(brokers) 

# @router.post("/categorias")  
def sync_categorias(session: SessionDep):
    categorias = get_categorias_mysql(session)

    if not categorias:
        raise HTTPException(400, "No hay categorias para sincronizar")
    ensure_table("analytics_konnect", "categorias", SCHEMAS["categorias"])
    truncate_table("analytics_konnect", "categorias")
    insert_rows("analytics_konnect", "categorias", categorias)

    # return { "status": "ok", "rows_synced": len(categorias) }
    return len(categorias) 

# @router.post("/estatus_tramites")
def sync_estatus_tramites(session: SessionDep):
    estatus_tramites = get_estatus_tramites_mysql(session)

    if not estatus_tramites:
        raise HTTPException(400, "No hay estatus_tramites para sincronizar")
    ensure_table("analytics_konnect", "estatus_tramites", SCHEMAS["estatus_tramites"])
    truncate_table("analytics_konnect", "estatus_tramites")
    insert_rows("analytics_konnect", "estatus_tramites", estatus_tramites)

    # return { "status": "ok", "rows_synced": len(estatus_tramites) }
    return len(estatus_tramites) 

# @router.post("/cotizacion")
def sync_cotizacion(session: SessionDep):
    cotizacion = get_cotizacion_mysql(session)

    if not cotizacion:
        raise HTTPException(400, "No hay cotizacion para sincronizar")
    ensure_table("analytics_konnect", "cotizacion", SCHEMAS["cotizacion"])
    truncate_table("analytics_konnect", "cotizacion")
    insert_rows("analytics_konnect", "cotizacion", cotizacion)

    # return { "status": "ok", "rows_synced": len(cotizacion) }
    return len(cotizacion) 

# @router.post("/estatus_tramites")
def sync_productos(session: SessionDep):
    productos = get_productos_mysql(session)

    if not productos:
        raise HTTPException(400, "No hay productos para sincronizar")
    ensure_table("analytics_konnect", "productos", SCHEMAS["productos"])
    truncate_table("analytics_konnect", "productos")
    insert_rows("analytics_konnect", "productos", productos)

    # return { "status": "ok", "rows_synced": len(productos) }
    return len(productos) 


# @router.post("/financieras")
def sync_financieras(session: SessionDep):
    financieras = get_financieras_mysql(session)

    if not financieras:
        raise HTTPException(400, "No hay financieras para sincronizar")
    ensure_table("analytics_konnect", "financieras", SCHEMAS["financieras"])
    truncate_table("analytics_konnect", "financieras")
    insert_rows("analytics_konnect", "financieras", financieras)

    # return { "status": "ok", "rows_synced": len(financieras) }
    return len(financieras) 

# @router.post("/sedes")
def sync_sedes(session: SessionDep):
    sedes = get_sedes_mysql(session)

    if not sedes:
        raise HTTPException(400, "No hay sedes para sincronizar")
    ensure_table("analytics_konnect", "sedes", SCHEMAS["sedes"])
    truncate_table("analytics_konnect", "sedes")
    insert_rows("analytics_konnect", "sedes", sedes)

    # return {"status": "ok", "rows_synced": len(sedes)}
    return len(sedes) 

# @router.post("/brokers")  
def sync_subCategorias(session: SessionDep):
    subCategorias = get_subCategorias_mysql(session)

    if not subCategorias:
        raise HTTPException(400, "No hay subCategorias para sincronizar")
    ensure_table("analytics_konnect", "subCategorias", SCHEMAS["subCategorias"])
    truncate_table("analytics_konnect", "subCategorias")
    insert_rows("analytics_konnect", "subCategorias", subCategorias)

    # return { "status": "ok", "rows_synced": len(subCategorias) }
    return len(subCategorias) 

# @router.post("/usuarios")
def sync_usuarios(session: SessionDep):
    usuarios = get_usuarios_mysql(session)

    if not usuarios:
        raise HTTPException(400, "No hay usuarios para sincronizar")
    ensure_table("analytics_konnect", "usuarios", SCHEMAS["usuarios"])
    truncate_table("analytics_konnect", "usuarios")
    insert_rows("analytics_konnect", "usuarios", usuarios)

    # return {"status": "ok", "rows_synced": len(usuarios)}
    return len(usuarios) 