from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header
from sqlalchemy import text
from sqlmodel import select
from jinja2 import Environment, FileSystemLoader
import os
import shutil
import base64

from datetime import date, timedelta
from sqlmodel import select
from app.db import SessionDep
from app.models import CorreosPagos, Cotizacion, Productos

from app.db import SessionDep
from app.models import Usuarios
from app.routers.bigQuery.dashboard import ( sync_brokers, sync_categorias, sync_cotizacion, sync_estatus_tramites, sync_financieras,
                                             sync_productos, sync_sedes, sync_subCategorias, sync_usuarios)
from utils.email import enviar_correo_informativo, enviar_correo_simple

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

def validar_cron_token_bq(x_cron_token: str = Header(None)):

    if not os.getenv("CRON_SECRET_BQ"):
        raise HTTPException(status_code=500, detail="Error de configuración en el servidor")
    if not x_cron_token:
        raise HTTPException(status_code=400, detail="X Token requerido")

    if x_cron_token != os.getenv("CRON_SECRET_BQ"):
        raise HTTPException(status_code=401, detail="X Token inválido")
# 🚀 ENDPOINT PRINCIPAL
@router.delete("/cotizaciones/borrar-pruebas")
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

from datetime import date

from datetime import date

from datetime import date

@router.get("/cotizacion/utils/fecha-pago-vencida")
async def cotizaciones_fecha_pago_vencida(session: SessionDep):
    hoy = date.today()

    rows = session.exec(
        select(
            Cotizacion.id_cotizacion,
            Cotizacion.fecha_pago,
            Cotizacion.id_financiera,
            Productos.nombre.label("producto"),
            Cotizacion.monto,
            CorreosPagos.correo
        )
        .join(
            Productos,
            Productos.id == Cotizacion.producto
        )
        .outerjoin(   # 👈 ESTO ES LA CLAVE
            CorreosPagos,
            CorreosPagos.id_financiera == Cotizacion.id_financiera
        )
        .where(
            Cotizacion.estatus == 11,
            Cotizacion.fecha_pago.is_not(None),
            Cotizacion.fecha_pago <= hoy
        )
    ).all()

    cotizaciones = {}

    for r in rows:
        if r.id_cotizacion not in cotizaciones:
            cotizaciones[r.id_cotizacion] = {
                "id_cotizacion": r.id_cotizacion,
                "fecha_pago": r.fecha_pago,
                "id_financiera": r.id_financiera,
                "producto": r.producto,
                "monto": r.monto,
                "correos": []
            }

        # Solo agregar si existe correo (porque puede venir None)
        if r.correo:
            if r.correo not in cotizaciones[r.id_cotizacion]["correos"]:
                cotizaciones[r.id_cotizacion]["correos"].append(r.correo)

    return {
        "total": len(cotizaciones),
        "cotizaciones": list(cotizaciones.values())
    }


@router.post("/dashboard")
async def sync_all(session: SessionDep, background_tasks: BackgroundTasks, _ = Depends(validar_cron_token_bq)):
    
    background_tasks.add_task(syncAllDashboard, session)
    return {
        "Estatus": "Sincronizaicon iniciada"
    }

def syncAllDashboard(session):
    results = {}

    results["brokers"] = sync_brokers(session)
    results["cotizacion"] = sync_cotizacion(session)
    results["categorias"] = sync_categorias(session)
    results["estatus_tramites"] = sync_estatus_tramites(session)
    results["financieras"] = sync_financieras(session)
    results["productos"] = sync_productos(session)
    results["sedes"] = sync_sedes(session)
    results["subCategorias"] = sync_subCategorias(session)
    results["usuarios"] = sync_usuarios(session)
    print(results)
    return {
        "status": "ok",
        "synced": results
    }

@router.post("/reporte-socios")
async def reporte_socios(
    session: SessionDep,
    background_tasks: BackgroundTasks,
    _ = Depends(validar_cron_token)
):
    statement = text("""
        SELECT 
            u.id,         
            u.nombre,
            u.email,
            b.nombre AS broker,
            s.nombre AS sede,
            u.celular
        FROM usuarios u
        INNER JOIN brokers b on b.id = u.id_broker
        INNER JOIN sedes s on s.id = u.id_sede
        WHERE u.id_financiera IS NULL
        AND u.id NOT IN (1,2,9,14,15,23,42,43)
        ORDER BY u.id
    """)

    usuarios = session.exec(statement).all()

    if not usuarios:
        return {"message": "No hay usuarios para enviar."}

    datos_tabla = []
    for u in usuarios:
        datos_tabla.append({
            "id": u[0],
            "nombre": u[1],
            "email": u[2],
            "broker": u[3],
            "sede": u[4],
            "celular": u[5]
        })

    correos_query = text("SELECT correo FROM correos")
    correos = session.exec(correos_query).all()

    # lista_correos = [c[0] for c in correos]

    lista_correos = ["ij.innovaciones@gmail.com",
        "info@konnect.mx", 
        "ara.castro@konnect.mx",
        "kfigueroa@konnect.mx"
        ]

    if not lista_correos:
        return {"message": "No hay correos destino."}

    img_path = os.path.join(ruta_base, "utils", "static", "firma.png")
    imagen_b64 = ""

    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            imagen_b64 = base64.b64encode(f.read()).decode("utf-8")

    try:
        template = env.get_template("reporte_socios.html")
        html_content = template.render(
            usuarios=datos_tabla,
            total=len(datos_tabla),
            imagen_b64=imagen_b64
        )
    except Exception as e:
        return {"error_template": str(e)}

 
    background_tasks.add_task(
        enviar_correo_simple,
        html_content,
        lista_correos,
        "Konnect 📊 Catálogo de Socios"
    )

    print("📧 Enviado a:", lista_correos)
    print("📊 Total usuarios:", len(datos_tabla))

    return {
        "status": "success",
        "enviado_a": lista_correos,
        "total": len(datos_tabla)
    }

@router.post("/reporte-vencimientos")
async def reporte_vencimientos(
    session: SessionDep, 
    background_tasks: BackgroundTasks, 
    _ = Depends(validar_cron_token)
):
    hoy = date.today()

    # 🔹 Traer usuarios cuya fecha de último pago cumple 1 año antes de fin de mes
    statement = text("""
        SELECT id, nombre, email, celular, membresia, f_ultimo_pago
        FROM usuarios
        WHERE DATE_ADD(f_ultimo_pago, INTERVAL 1 YEAR) <= LAST_DAY(CURDATE())
    """)
    usuarios = session.exec(statement).all()

    if not usuarios:
        return {"message": "No hay usuarios con pagos registrados que cumplan 1 año."}

    datos_tabla = []

    for u in usuarios:
        fecha_vencimiento = u.f_ultimo_pago + timedelta(days=365)

        datos_tabla.append({
            "nombre": u.nombre,
            "email": u.email,
            "vencimiento": fecha_vencimiento.strftime("%d/%m/%Y"),
            "es_vencido": fecha_vencimiento < hoy,
            "celular": u.celular,
            "membresia": u.membresia,
            "f_ultimo_pago": u.f_ultimo_pago.strftime("%d/%m/%Y") if u.f_ultimo_pago else None
        })

    if not datos_tabla:
        return {"message": "No hay cuentas vencidas ni por vencer este mes."}

    lista_correos = [
        "ij.innovaciones@gmail.com",
        "info@konnect.mx", 
        "ara.castro@konnect.mx",
        "kfigueroa@konnect.mx"
        ]

    img_path = os.path.join(ruta_base, "utils", "static", "firma.png")
    imagen_b64 = ""
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            imagen_b64 = base64.b64encode(f.read()).decode("utf-8")

    meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_nombre = meses_es[hoy.month - 1]

    try:
        template = env.get_template("reporte_vencidos.html")
        html_content = template.render(
            usuarios=datos_tabla,
            mes_reporte=f"{mes_nombre} {hoy.year}",
            imagen_b64=imagen_b64
        )
    except Exception as e:
        return {"error_template": str(e)}

    background_tasks.add_task(
        enviar_correo_simple,
        html_content,
        lista_correos,
        f"Konnect  Reporte de Vencimientos - {mes_nombre}"
    )

    print("📧 Enviado a:", lista_correos)
    print("📊 Total registros:", len(datos_tabla))

    return {
        "status": "success",
        "enviado_a": lista_correos,
        "total_registros": len(datos_tabla),
        "mes": mes_nombre
    }