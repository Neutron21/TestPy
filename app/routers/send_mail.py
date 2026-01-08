import base64
import os
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Body, Request
from app.models import BodyMail, Brokers, Correos, Cotizacion, Financieras, ReqMail, Sedes, Usuarios, Productos
from sqlmodel import select, text
from app.db import SessionDep
from utils.email import enviar_correo, notificacion_if, enviar_correo_dispersion, enviar_correo_informativo
from app.utils.logger_config import logger
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os


router = APIRouter(tags=["SendMails"])

ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_templates = os.path.join(ruta_base, "templates")
env = Environment(loader=FileSystemLoader(ruta_templates))


def obtener_jefes(user_id: int, session) -> List[Usuarios]:
    query = text("""
        WITH RECURSIVE superiors AS (
            SELECT id, email, id_superior FROM usuarios WHERE id = :user_id
            UNION ALL
            SELECT u.id, u.email, u.id_superior
            FROM usuarios u
            INNER JOIN superiors s ON s.id_superior = u.id
        )
        SELECT email FROM superiors WHERE id != :user_id
    """)
    result = session.exec(query.params(user_id=user_id)).all()
    return [row[0] for row in result]



@router.post("/enviar-correo")
async def enviar_mail(request: ReqMail, session: SessionDep, background_tasks: BackgroundTasks):
    try:
        query_cotizacion = select(Cotizacion).where(Cotizacion.id_cotizacion == request.numCotizacion)
        cotizacion = session.exec(query_cotizacion).first()
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")

        query_producto = select(Productos).where(Productos.id == cotizacion.producto)
        producto = session.exec(query_producto).first()

        if cotizacion.id_financiera == 14:
            query_correos = select(Correos.correo).where(
                (Correos.id_financiera == cotizacion.id_financiera) &
                (Correos.v_mail == 1) &
                (Correos.categoria_id == producto.id_categoria)
            )
        else:
            query_correos = select(Correos.correo).where(
                (Correos.id_financiera == cotizacion.id_financiera) & (Correos.v_mail == 1)
            )

        query_broker = select(Brokers.nombre).where(Brokers.id == cotizacion.broker)
        query_sede = select(Sedes.nombre).where(Sedes.id == cotizacion.sede)
        query_fin = select(Financieras).where(Financieras.id == cotizacion.id_financiera)
        query_usuario = select(Usuarios).where(Usuarios.email == cotizacion.id_usuario)
        correos_superiores = obtener_jefes(cotizacion.id_user, session)
        usuario = session.exec(query_usuario).first()

        correosIF = session.exec(query_correos).all()
        broker = session.exec(query_broker).first()
        sede = session.exec(query_sede).first()
        financiera = session.exec(query_fin).first()

        cotizacionBytes = str(cotizacion.id_cotizacion).encode('utf-8')
        base64_bytes = base64.b64encode(cotizacionBytes)
        bodyMail = BodyMail(
            OpCliente=cotizacion.OpCliente,
            brokerName=broker,
            cliente=cotizacion.nombre,
            emailUser=cotizacion.id_usuario,
            ifName=financiera.nombre,
            isNew=request.isNew,
            listaMails=correosIF,
            monto=f"{cotizacion.monto:,.0f}",
            numCotizacion=cotizacion.id_cotizacion,
            productoName=producto.nombre,
            rfc=cotizacion.rfc.upper(),
            sedeName=sede,
            userName=usuario.nombre,
            cotizacionB64=base64_bytes.decode('utf-8'),
            ingresos=f"{cotizacion.ingresos:,.0f}",
            tipoPersona=cotizacion.tipo_persona.capitalize(),
            antiguedadEmpresa=cotizacion.antiguedad_empresa,
            edad=cotizacion.edad,
            plazo=cotizacion.plazo,
            celular=usuario.celular,
            destinoCredito=cotizacion.destinoCredito
        )

        correosKonfio = []
        if request.isNew and cotizacion.id_financiera == 1:
            correosKonfio = ["maria.mendoza@konfio.mx", "luis.ramirez@konfio.mx"]

        correos = list(set(correosIF + correosKonfio + correos_superiores + ["ara.castro@konnect.mx", "gerencia.operativa@konnect.mx"]))

        template_name = "cotizacion.html" if request.isNew else "updateFiles.html"
        withLink = financiera.tipo == 'M'

        template = env.get_template(template_name)
        html_content = template.render(**vars(bodyMail), isLink=withLink)

        background_tasks.add_task(enviar_correo, bodyMail, html_content, correos)

        return {"mensaje": "Solicitud recibida, el correo se está enviando en segundo plano."}
    except Exception as e:
        logger.error(f"Request :( {request}")
        logger.error(f"Error al preparar correo: {str(e)}")
        return {"mensaje": str(e)}



@router.post("/comentario-if")
async def enviar_mail(session: SessionDep, idCotizacion: int = Body(..., embed=True)):
    query_cotizacion = select(Cotizacion).where(Cotizacion.id_cotizacion == idCotizacion)
    cotizacion = session.exec(query_cotizacion).first()
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    correos_superiores = obtener_jefes(cotizacion.id_user, session)
    correos = list(set([cotizacion.id_usuario] + correos_superiores))
    request = dict(folioKonnect=idCotizacion, cliente=cotizacion.nombre)

    template = env.get_template("comentarioIF.html")
    html_content = template.render(**request)
    resultado = notificacion_if(cotizacion.nombre, html_content, correos)

    return {"mensaje": resultado}


@router.post("/correo-dispersion")
def correo_dispersion(data: dict, session: SessionDep):
    id_cotizacion = data.get("idCotizacion")
    if not id_cotizacion:
        raise HTTPException(status_code=400, detail="idCotizacion requerido")

    cotizacion = session.get(Cotizacion, id_cotizacion)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    if cotizacion.estatus != 7:
        raise HTTPException(status_code=400, detail="La cotización no está en estatus Dispersión")

    correos = [
        "kfigueroa@konnect.mx", "ara.castro@konnect.mx",
        "gerencia.operativa@konnect.mx", "gerencia.corporativa@konnect.mx"
    ]

    request = dict(folioKonnect=id_cotizacion, cliente=cotizacion.nombre)
    template = env.get_template("dispersion.html")
    html_content = template.render(**request)

    enviar_correo_dispersion(cotizacion, html_content, correos)

    return {"ok": True, "message": "Correo de dispersión enviado correctamente"}


@router.post("/recordatorio-estatus")
async def enviar_correo_recordatorio(session: SessionDep, tipo: Optional[int],background_tasks: BackgroundTasks, request: Request,):
    # 🔐 Seguridad
    token = request.headers.get("x-cron-token")
    if not token:
        raise HTTPException(status_code=400, detail="X Token requerido")

    if token != os.getenv("CRON_SECRET"):
        raise HTTPException(status_code=401, detail="X Token inválido")
    
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
