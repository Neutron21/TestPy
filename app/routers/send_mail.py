import base64
import os
from fastapi import APIRouter
from app.models import Correos, ReqMail
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
    # Variables que vas a pasar a la plantilla
    context = {
        "isNew":"true",
        "emailUser":"ij.innovaciones@gmail.com",
        "cliente":" ",
        "financiera":13,
        "rfc":"cala930521",
        "monto":500000,
        "producto":"ARRENDAMIENTO PURO PF",
        "broker":'',
        "sede":'',
        "userName":'',
        "numCotizacion":219,
        "institucion":"Arrenda+",
        "OpCliente":"CDMX",
        "update":1,
        "listaMails":[]
        }
    query = select(Correos.mail).where(
        (Correos.id_financiera == request.financiera) & (Correos.activo == 1)
    )
    # result = session.exec(query).all()
    correos = session.exec(query).all()
    # correos = [row[0] for row in result]
    print("CORREOS ")
    print(correos)
    cotizacionBytes = str(request.numCotizacion).encode('utf-8')
    base64_bytes = base64.b64encode(cotizacionBytes)
    request.cotizacionB64 = base64_bytes.decode('utf-8')
    # Carga y renderiza la plantilla con variables
    template = env.get_template("cotizacion.html")
    html_content = template.render(request)

    destinatario = request.emailUser
    resultado = enviar_correo(destinatario, html_content, correos)  # Ajuste para enviar HTML
    return {"mensaje": resultado}
