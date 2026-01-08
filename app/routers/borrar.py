from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text
import os
import shutil

from app.db import SessionDep

router = APIRouter(tags=["Borrar"])

# 🔎 Obtiene IDs de cotizaciones que contienen "prueba"
def obtener_ids_prueba(session):
    result = session.execute(text("""
        SELECT id_cotizacion
        FROM cotizacion
        WHERE LOWER(nombre) LIKE '%prueba%'
    """))

    ids = [str(row.id_cotizacion) for row in result]
    return ids


# 🗑 Borra carpetas por ID de cotización
def borrar_carpetas(ids):
    base_path = os.getenv("RUTA_COTIZACIONES")

    if not base_path:
        return 0

    eliminadas = 0

    for cot_id in ids:
        ruta = os.path.join(base_path, cot_id)
        if os.path.exists(ruta):
            shutil.rmtree(ruta)
            eliminadas += 1

    return eliminadas


# 🧨 Borra registros en BD
def borrar_cotizaciones_prueba(session):
    result = session.execute(text("""
        DELETE FROM cotizacion
        WHERE LOWER(nombre) LIKE '%prueba%'
    """))

    return result.rowcount


# 🚀 ENDPOINT PRINCIPAL
@router.post("/cotizaciones/borrar-pruebas")
def borrar_pruebas(request: Request, session: SessionDep):
    # 🔐 Seguridad
    token = request.headers.get("x-cron-token")
    if not token:
        raise HTTPException(status_code=400, detail="X Token requerido")

    if token != os.getenv("CRON_SECRET"):
        raise HTTPException(status_code=401, detail="X Token inválido")

    # 🔎 1. Obtener IDs
    ids = obtener_ids_prueba(session)

    if not ids:
        return {
            "mensaje": "No hay cotizaciones de prueba",
            "total_bd": 0,
            "carpetas_borradas": 0
        }

    # 🗑 2. Borrar carpetas
    carpetas_borradas = borrar_carpetas(ids)

    # 🧨 3. Borrar BD
    total_bd = borrar_cotizaciones_prueba(session)

    session.commit()

    return {
        "mensaje": "Cotizaciones de prueba eliminadas correctamente",
        "total_bd": total_bd,
        "carpetas_borradas": carpetas_borradas
    }
