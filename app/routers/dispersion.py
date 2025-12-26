from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.db import SessionDep
from app.models import Cotizacion
from utils.email import enviar_correo_dispersion
from app.utils.logger_config import logger
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import os

# 🔹 Cargar variables de entorno
print("BREVO_URL:", os.getenv("BREVO_LINK"))

router = APIRouter(tags=["Cotizaciones"])

# 🔹 Configuración de Jinja2 (ESTO FALTABA)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=True
)

@router.post("/cotizaciones/correo-dispersion")
def correo_dispersion(
    data: dict,
    session: SessionDep,
    background_tasks: BackgroundTasks
):
    # 🔹 Validar input
    id_cotizacion = data.get("idCotizacion")
    if not id_cotizacion:
        raise HTTPException(status_code=400, detail="idCotizacion requerido")

    # 🔹 Obtener cotización
    cotizacion: Cotizacion = session.get(Cotizacion, id_cotizacion)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    # 🔹 Validar estatus Dispersión
    if cotizacion.estatus != 7:
        raise HTTPException(
            status_code=400,
            detail="La cotización no está en estatus Dispersión"
        )

    # 🔹 Correos destino
    correos: List[str] = [
        "victor.hugo.silva01@gmail.com"
    ]

    # 🔹 Renderizar template
    template = env.get_template("dispersion.html")
    html_content = template.render(cotizacion=cotizacion)

    # 🔹 Enviar correo en segundo plano
    try:
        background_tasks.add_task(
            enviar_correo_dispersion,
            cotizacion,
            html_content,
            correos
        )

        logger.info(
            f"📧 Correo de dispersión solicitado | Cotización {id_cotizacion} | Correos: {correos}"
        )

        return {
            "ok": True,
            "message": "Correo de dispersión solicitado correctamente"
        }

    except Exception as e:
        logger.error(
            f"❌ Error al solicitar correo de dispersión | Cotización {id_cotizacion}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="Error al solicitar correo de dispersión"
        )
