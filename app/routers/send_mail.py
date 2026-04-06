import base64
import os
from types import SimpleNamespace
from typing import List
from fastapi import APIRouter, BackgroundTasks, HTTPException, Body, Request
from app.models import BodyMail, Brokers, Correos, Cotizacion, Financieras, ReqMail, Sedes, Usuarios, Productos, ReqMailComentarioDir
from sqlmodel import select, text
from app.db import SessionDep
from utils.email import enviar_correo, enviar_correo_informativo, enviar_correo_simple, notificacion_if, enviar_correo_dispersion, send_mail_comment
from app.utils.logger_config import logger
from jinja2 import Environment, FileSystemLoader
from app.models import Productos



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

def obtener_mails_ifs(cotizacion: Cotizacion, session) -> List[str]:

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
    correosIF = session.exec(query_correos).all()
    return correosIF

@router.post("/enviar-correo")
async def enviar_mail(request: ReqMail, session: SessionDep, background_tasks: BackgroundTasks):
    try:
        query_cotizacion = select(Cotizacion).where(Cotizacion.id_cotizacion == request.numCotizacion)
        cotizacion = session.exec(query_cotizacion).first()
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")

        query_producto = select(Productos).where(Productos.id == cotizacion.producto)
        producto = session.exec(query_producto).first()

        query_broker = select(Brokers.nombre).where(Brokers.id == cotizacion.broker)
        query_sede = select(Sedes.nombre).where(Sedes.id == cotizacion.sede)
        query_fin = select(Financieras).where(Financieras.id == cotizacion.id_financiera)
        query_usuario = select(Usuarios).where(Usuarios.email == cotizacion.id_usuario)
        correos_superiores = obtener_jefes(cotizacion.id_user, session)
        usuario = session.exec(query_usuario).first()

        correosIF = obtener_mails_ifs(cotizacion, session)
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
async def send_comentario(session: SessionDep, idCotizacion: int = Body(..., embed=True)):
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
def mail_dispersion(data: dict, session: SessionDep):
    id_cotizacion = data.get("idCotizacion")
    if not id_cotizacion:
        raise HTTPException(status_code=400, detail="idCotizacion requerido")

    cotizacion = session.get(Cotizacion, id_cotizacion)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    producto = session.get(Productos, cotizacion.producto)
    if not producto:
       raise HTTPException(status_code=404, detail="Producto no encontrado")

    if cotizacion.estatus != 7:
        raise HTTPException(status_code=400, detail="La cotización no está en estatus Dispersión")
    correosIfs = obtener_mails_ifs(cotizacion, session)
    correos = list(set(correosIfs + [ 
        "kfigueroa@konnect.mx", "ara.castro@konnect.mx",
        "gerencia.operativa@konnect.mx", "gerencia.corporativa@konnect.mx" 
        ]))
  
    request = dict(folioKonnect=id_cotizacion, cliente=cotizacion.nombre, producto=producto.nombre)
    
    template = env.get_template("dispersion.html")
    html_content = template.render(**request)

    enviar_correo_dispersion(cotizacion, html_content, correos)

    return {"ok": True, "message": "Correo de dispersión enviado correctamente"}

@router.post("/correo-nuevo-usuario/{user_id}")
def enviar_correo_nuevo_usuario(
    user_id: int,
    session: SessionDep,
    background_tasks: BackgroundTasks
):

    usuario = session.get(Usuarios, user_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 🔥 SOLO enviar si es "Sin financiera"
    if usuario.id_financiera is not None:
        return {
            "ok": True,
            "mensaje": "Tiene financiera asignada, no se envía correo"
        }

    broker = session.get(Brokers, usuario.id_broker) if usuario.id_broker else None
    sede = session.get(Sedes, usuario.id_sede) if usuario.id_sede else None

    # 🔥 Obtener correos de financieras 32, 11, 12 y 37
    financieras_utm_custom = [32, 11, 12, 37]

    correos_financieras = session.query(Usuarios.email).filter(
        Usuarios.id_financiera.in_(financieras_utm_custom)
    ).all()

    correos_db = [correo[0] for correo in correos_financieras]
    
    if not correos_db:
        return {
            "ok": False,
            "mensaje": "No se encontraron correos para enviar"
        }
    correos_konnect = [
        "victor.hugo.silva01@gmail.com",
        "ara.castro@konnect.mx",
        "kfigueroa@konnect.mx"
    ]

    # 🔥 Lista final sin duplicados, sin None y sin vacíos
    lista_correos = list({
        correo.strip()
        for correo in (correos_db + correos_konnect)
        if correo and correo.strip()
    })

    template = env.get_template("usuario.html")

    html_content = template.render(
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.celular,
        broker=broker.nombre if broker else "N/A",
        sede=sede.nombre if sede else "N/A",
        financiera="Sin financiera"
    )

    print("📩 Enviando correo para usuario:", usuario.id)
    print("📨 Destinatarios:", lista_correos)

    background_tasks.add_task(
        enviar_correo_simple,
        html_content,
        lista_correos,
        f"🆕 Nuevo Usuario - {usuario.nombre}"
    )

    return {
        "ok": True,
        "mensaje": "Correo enviado correctamente",
        "destinatarios": lista_correos
    }
    
@router.post("/comentario-direccion")
def mail_comentario_direccion(data: ReqMailComentarioDir, session: SessionDep):
   
    cotizacion = session.get(Cotizacion, data.idCotizacion)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
 
    print(f"BODY: {data}")
    request_mail = SimpleNamespace(
        id_cotizacion = data.idCotizacion,
        cliente = cotizacion.nombre,
        mensaje = data.message
    )
    # correos = obtener_jefes(cotizacion.id_user ,session)
    correos = [cotizacion.id_usuario]
    template = env.get_template("comentarioDir.html")

    html_content = template.render(
        cliente = cotizacion.nombre,
        mensaje = data.message,
        folioKonnect = data.idCotizacion
    )
    send_mail_comment(request_mail, correos, html_content)

    return {"ok": True, "message": "Correo de dispersión enviado correctamente"}