import os
from fastapi import APIRouter
from utils.email import enviar_correo
from jinja2 import Environment, FileSystemLoader

router = APIRouter(tags=["Correo"])

# Carga el entorno Jinja2 apuntando a la carpeta templates
ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_templates = os.path.join(ruta_base, "templates")
env = Environment(loader=FileSystemLoader(ruta_templates))

@router.post("/enviar-correo")
async def enviar_mail():
    # Variables que vas a pasar a la plantilla
    context = {
        "cliente": "Juan Pérez",
        "rfc": "JUAP890123HDF",
        "institucion": "Banco X",
        "monto": "$100,000",
        "producto": "Crédito Personal",
        "broker": "Carlos López",
        "sede": "CDMX",
        "OpCliente": "Operativa A",
        "numCotizacion": "KON-12345",
        "userName": "Victor Silva",
        "cotizacionB64": "archivo_base64.pdf"
    }

    # Carga y renderiza la plantilla con variables
    template = env.get_template("cotizacion.html")
    html_content = template.render(context)

    destinatario = "victor.hugo.silva01@gmail.com"
    resultado = enviar_correo(destinatario, html_content)  # Ajuste para enviar HTML
    return {"mensaje": resultado}
