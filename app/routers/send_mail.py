import base64
import os
from fastapi import APIRouter
from app.models import BodyMail, Brokers, Correos, Cotizacion, Financieras, ReqMail, Sedes
from sqlmodel import select
from app.db import SessionDep
from utils.email import enviar_correo
from jinja2 import Environment, FileSystemLoader

router = APIRouter(tags=["SendMails"])

# Carga el entorno Jinja2 apuntando a la carpeta templates
ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_templates = os.path.join(ruta_base, "templates")
env = Environment(loader=FileSystemLoader(ruta_templates))

@router.post("/enviar-correo")
async def enviar_mail(request: ReqMail, session: SessionDep):
  
    query_cotizacion =  select(Cotizacion).where(Cotizacion.id_cotizacion == request.numCotizacion)
    cotizacion = session.exec(query_cotizacion).first()
    print(f"Req: {cotizacion}")

    query_correos = select(Correos.mail).where((Correos.id_financiera == cotizacion.id_financiera) & (Correos.activo == 1))
    query_broker = select(Brokers.nombre).where(Brokers.id == cotizacion.broker)
    query_sede = select(Sedes.nombre).where(Sedes.id == cotizacion.sede)
    query_fin = select(Financieras.nombre).where(Financieras.id == cotizacion.id_financiera)

    correos = session.exec(query_correos).all()
    broker = session.exec(query_broker).first()
    sede = session.exec(query_sede).first()
    financiera = session.exec(query_fin).first()

    cotizacionBytes = str(cotizacion.id_cotizacion).encode('utf-8')
    base64_bytes = base64.b64encode(cotizacionBytes)
    bodyMail = BodyMail(
        OpCliente = cotizacion.OpCliente,
        brokerName = broker,
        cliente = cotizacion.nombre,
        emailUser = cotizacion.id_usuario,
        ifName = financiera,
        isNew = request.isNew,
        listaMails = correos,
        monto = f"{cotizacion.monto:,.0f}",
        numCotizacion = cotizacion.id_cotizacion,
        productoName = request.producto,
        rfc = cotizacion.rfc.upper(),
        sedeName = sede,
        userName = request.userName,
        cotizacionB64 = base64_bytes.decode('utf-8'),
        ingresos = f"{cotizacion.ingresos:,.0f}",
        tipoPersona = cotizacion.tipo_persona.capitalize(),
        antiguedadEmpresa =  cotizacion.antiguedad_empresa,
        edad = cotizacion.edad,
        plazo = cotizacion.plazo
    )
    print(f"bodyMail: {bodyMail}")

    # Carga y renderiza la plantilla con variables
    template = env.get_template("cotizacion.html")
    html_content = template.render(bodyMail)

    resultado = enviar_correo(bodyMail, html_content, correos)  # Ajuste para enviar HTML
    return {"mensaje": resultado}
    # return {"mensaje": "OK"}
