from fastapi import APIRouter, HTTPException
from app.db import SessionDep
from app.routers.bigQuery.service_mysql import (get_brokers_mysql, get_cotizacion_mysql, get_estatus_tramites_mysql, 
                                                get_financieras_mysql, get_productos_mysql, get_sedes_mysql, get_usuarios_mysql,
                                                get_categorias_mysql, get_subCategorias_mysql, get_membresias_mysql,
                                                get_track_status_mysql, get_comentarios_mysql)
from app.routers.bigQuery.service_bQ import (
    ensure_table,
    truncate_table,
    insert_rows,
    SCHEMAS
)

router = APIRouter(prefix="/sync/bigquery", tags=["BigQuery Sync"])

def sync_brokers(session: SessionDep):
    print("Iniciando sincronización de brokers")
    brokers = get_brokers_mysql(session)

    if not brokers:
        raise HTTPException(400, "No hay brokers para sincronizar")
    print(f"Broker rows obtenidas: {len(brokers)}")
    ensure_table("analytics_konnect", "brokers", SCHEMAS["brokers"])
    truncate_table("analytics_konnect", "brokers")
    insert_rows("analytics_konnect", "brokers", brokers)

    return len(brokers)

def sync_categorias(session: SessionDep):
    categorias = get_categorias_mysql(session)

    if not categorias:
        raise HTTPException(400, "No hay categorias para sincronizar")
    ensure_table("analytics_konnect", "categorias", SCHEMAS["categorias"])
    truncate_table("analytics_konnect", "categorias")
    insert_rows("analytics_konnect", "categorias", categorias)

    return len(categorias) 

def sync_estatus_tramites(session: SessionDep):
    estatus_tramites = get_estatus_tramites_mysql(session)

    if not estatus_tramites:
        raise HTTPException(400, "No hay estatus_tramites para sincronizar")
    ensure_table("analytics_konnect", "estatus_tramites", SCHEMAS["estatus_tramites"])
    truncate_table("analytics_konnect", "estatus_tramites")
    insert_rows("analytics_konnect", "estatus_tramites", estatus_tramites)

    return len(estatus_tramites) 


def sync_cotizacion(session: SessionDep):
    cotizacion = get_cotizacion_mysql(session)

    if not cotizacion:
        raise HTTPException(400, "No hay cotizacion para sincronizar")
    ensure_table("analytics_konnect", "cotizacion", SCHEMAS["cotizacion"])
    truncate_table("analytics_konnect", "cotizacion")
    insert_rows("analytics_konnect", "cotizacion", cotizacion)

    return len(cotizacion) 


def sync_productos(session: SessionDep):
    productos = get_productos_mysql(session)

    if not productos:
        raise HTTPException(400, "No hay productos para sincronizar")
    ensure_table("analytics_konnect", "productos", SCHEMAS["productos"])
    truncate_table("analytics_konnect", "productos")
    insert_rows("analytics_konnect", "productos", productos)

    return len(productos) 


def sync_financieras(session: SessionDep):
    financieras = get_financieras_mysql(session)

    if not financieras:
        raise HTTPException(400, "No hay financieras para sincronizar")
    ensure_table("analytics_konnect", "financieras", SCHEMAS["financieras"])
    truncate_table("analytics_konnect", "financieras")
    insert_rows("analytics_konnect", "financieras", financieras)

    return len(financieras) 


def sync_sedes(session: SessionDep):
    sedes = get_sedes_mysql(session)

    if not sedes:
        raise HTTPException(400, "No hay sedes para sincronizar")
    ensure_table("analytics_konnect", "sedes", SCHEMAS["sedes"])
    truncate_table("analytics_konnect", "sedes")
    insert_rows("analytics_konnect", "sedes", sedes)

    return len(sedes) 


def sync_subCategorias(session: SessionDep):
    subCategorias = get_subCategorias_mysql(session)

    if not subCategorias:
        raise HTTPException(400, "No hay subCategorias para sincronizar")
    ensure_table("analytics_konnect", "subCategorias", SCHEMAS["subCategorias"])
    truncate_table("analytics_konnect", "subCategorias")
    insert_rows("analytics_konnect", "subCategorias", subCategorias)

    return len(subCategorias) 


def sync_usuarios(session: SessionDep):
    print("Iniciando sincronización de usuarios")
    usuarios = get_usuarios_mysql(session)

    if not usuarios:
        raise HTTPException(400, "No hay usuarios para sincronizar")
    print(f"Usuarios rows obtenidas: {len(usuarios)}")
    ensure_table("analytics_konnect", "usuarios", SCHEMAS["usuarios"])
    truncate_table("analytics_konnect", "usuarios")
    insert_rows("analytics_konnect", "usuarios", usuarios)

    return len(usuarios)


def sync_membresias(session: SessionDep):
    print("Iniciando sincronización de membresias")
    membresias = get_membresias_mysql(session)

    if not membresias:
        raise HTTPException(400, "No hay membresias para sincronizar")
    print(f"Membresias rows obtenidas: {len(membresias)}")
    ensure_table("analytics_konnect", "membresias", SCHEMAS["membresias"])
    truncate_table("analytics_konnect", "membresias")
    insert_rows("analytics_konnect", "membresias", membresias)

    return len(membresias)


def sync_track_status(session: SessionDep):
    print("Iniciando sincronización de track_status")
    track_status = get_track_status_mysql(session)

    if not track_status:
        raise HTTPException(400, "No hay track_status para sincronizar")
    print(f"Track status rows obtenidas: {len(track_status)}")
    ensure_table("analytics_konnect", "track_status", SCHEMAS["track_status"])
    truncate_table("analytics_konnect", "track_status")
    insert_rows("analytics_konnect", "track_status", track_status)

    return len(track_status)


def sync_comentarios(session: SessionDep):
    print("Iniciando sincronización de comentarios")
    comentarios = get_comentarios_mysql(session)

    if not comentarios:
        raise HTTPException(400, "No hay comentarios para sincronizar")
    print(f"Comentarios rows obtenidas: {len(comentarios)}")
    ensure_table("analytics_konnect", "comentarios", SCHEMAS["comentarios"])
    truncate_table("analytics_konnect", "comentarios")
    insert_rows("analytics_konnect", "comentarios", comentarios)

    return len(comentarios)