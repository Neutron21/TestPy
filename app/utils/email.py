import base64

import requests
from email.mime.image import MIMEImage
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from app.utils.logger_config import logger
from app.models import ReqMail

BREVO_API_KEY = os.getenv("BREVO_KEY") 
BREVO_URL = os.getenv("BREVO_LINK")

def fillFirma():
    firma_path = os.path.join(os.path.dirname(__file__), "static", "firma.png")
   
    try:
        with open(firma_path, "rb") as img:
            firma_b64 = base64.b64encode(img.read()).decode()
    except FileNotFoundError:
        logger.error(f"Firma no encontrada: {firma_path}")
        firma_b64 = None
    
    return firma_b64

def enviar_correo(request: ReqMail, mensaje_html: str, correos: list[str]):
    destinatario = [request.emailUser]

    # Eliminar duplicados con el set y agregamos correo del usuario logueado
    correos_totales = list(set(correos + destinatario))
    print(f"--> CorreosTotales: {correos_totales}")
    
    tipo_solicitud = "Cliente" if request.isNew else "Actualización"
    subject = f"{tipo_solicitud}: {request.cliente} {request.rfc}"

    firma_path = os.path.join(os.path.dirname(__file__), "static", "firma.png")
   
    try:
        with open(firma_path, "rb") as img:
            firma_b64 = base64.b64encode(img.read()).decode()
    except FileNotFoundError:
        logger.error(f"Firma no encontrada: {firma_path}")
        firma_b64 = None
    # Armar payload
    data = {
        "sender": {
            "email": "web.app.no.reply@konnect.mx",
            "name": "Konnect"
        },
        "to": [{"email": e} for e in destinatario],
        "cc": [{"email": e} for e in correos],
        "subject": subject,
        "htmlContent": mensaje_html,
        "attachment": [
            {
                "name": "firma.png",
                "content": firma_b64
            }
        ]
    }
   
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    print("---> A punto de enviar a Brevo")
    try:
        res = requests.post(BREVO_URL, json=data, headers=headers)
        print(f"Brevo response: ({res.status_code}) {res.text}")
        # EL LOGGER NO SE VE EN CONSOLA SOLO EN EL ARCHIVO DE LOGS
        # logger.info(f"Brevo response: ({res.status_code}) {res.text}") 
    except Exception as e:
        logger.error(f"Brevo Ex: {data}")
        logger.error(f"❌ Error al enviar el correo: {str(e)}")

def notificacion_if(cliente: str, mensaje_html: str, correos: list[str]):

    firma_b64 = fillFirma()

    data = {
        "sender": {
            "email": "web.app.no.reply@konnect.mx",
            "name": "Konnect"
        },
        "to": [{"email": e} for e in correos],
        "subject": f"La IF comento sobre el cliente {cliente}",
        "htmlContent": mensaje_html,
        "attachment": [
            {
                "name": "firma.png",
                "content": firma_b64
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    try:
        res = requests.post(BREVO_URL, json=data, headers=headers)
        print(f"Brevo response: ({res.status_code}) {res.text}")
        return "Correo enviado con éxito."
    except Exception as e:
        logger.error(f"Request: {cliente} -- ")
        logger.error(f"❌ Error al enviar el correo FN(notificacion_if): {str(e)}")
        return f"Error al enviar el correo: {str(e)}"