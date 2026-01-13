from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Header
from sqlalchemy import text
from sqlmodel import select
from jinja2 import Environment, FileSystemLoader
import os
import shutil
import base64

from app.db import SessionDep
from app.models import Usuarios
from utils.email import enviar_correo_informativo

router = APIRouter(tags=["Tareas"])

ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_templates = os.path.join(ruta_base, "templates")
env = Environment(loader=FileSystemLoader(ruta_templates))

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

# 🔐 Seguridad
def validar_cron_token(x_cron_token: str = Header(None)):

    if not os.getenv("CRON_SECRET"):
        raise HTTPException(status_code=500, detail="Error de configuración en el servidor")
    if not x_cron_token:
        raise HTTPException(status_code=400, detail="X Token requerido")

    if x_cron_token != os.getenv("CRON_SECRET"):
        raise HTTPException(status_code=401, detail="X Token inválido")

# 🚀 ENDPOINT PRINCIPAL
@router.post("/cotizaciones/borrar-pruebas")
def borrar_pruebas(session: SessionDep, _ = Depends(validar_cron_token)):
    
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

@router.post("/recordatorio-estatus")
async def enviar_correo_recordatorio(session: SessionDep, tipo: Optional[int],background_tasks: BackgroundTasks, _ = Depends(validar_cron_token)):
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if tipo == 1:
        image_name = "orden.jpg"
        subject = "📌 ACTUALIZA TUS ESTATUS"
    elif tipo == 2:
        image_name = "estatus.jpg"
        subject = "🗓️ VIERNES DE ESTATUS"
    elif tipo == 3:
        image_name = "viernes.jpg"
        subject = "⏰ NO LO OLVIDES"
  
    img_path = os.path.join(BASE_DIR, "utils", "static", image_name)

    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail=f"No existe la imagen: {img_path}")

    with open(img_path, "rb") as f:
        imagen_b64 = base64.b64encode(f.read()).decode("utf-8")

    template = env.get_template("recordatorios.html")
    html_content = template.render()

    query_usuarios = select(Usuarios.email).where(Usuarios.nivel <= 3)
    correos = session.exec(query_usuarios).all()

    print("Correos que recibirán el recordatorio:", correos)

    background_tasks.add_task(enviar_correo_informativo, html_content, correos, subject, imagen_b64)
   
    return {"mensaje": "Proceso de envío iniciado"}
