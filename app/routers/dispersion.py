from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.db import SessionDep
from app.models import Cotizacion
from utils.email import enviar_correo_dispersion
from app.utils.logger_config import logger
from dotenv import load_dotenv
import os

load_dotenv()  # carga las variables del .env
print("BREVO_URL:", os.getenv("BREVO_LINK"))

router = APIRouter(tags=["Cotizaciones"])

@router.post("/cotizaciones/correo-dispersion")
def correo_dispersion(
    data: dict, 
    session: SessionDep, 
    background_tasks: BackgroundTasks
):
    """
    Envía un correo de dispersión para la cotización especificada.
    """

    id_cotizacion = data.get("idCotizacion")
    if not id_cotizacion:
        raise HTTPException(status_code=400, detail="idCotizacion requerido")

    cotizacion: Cotizacion = session.get(Cotizacion, id_cotizacion)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    if cotizacion.estatus != 7:
        raise HTTPException(
            status_code=400,
            detail="La cotización no está en estatus Dispersión"
        )

    correos: List[str] = [
        "victor.hugo.silva01@gmail.com"
    ]

    try:
        background_tasks.add_task(enviar_correo_dispersion, cotizacion, correos)
        logger.info(f"Correo de dispersión solicitado para Cotizacion ID: {id_cotizacion}, correos: {correos}")

        return {
            "ok": True,
            "message": "Correo de dispersión solicitado correctamente"
        }

    except Exception as e:
        logger.error(f"❌ Error al solicitar correo de dispersión para Cotizacion ID {id_cotizacion}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al solicitar correo de dispersión: {str(e)}")
