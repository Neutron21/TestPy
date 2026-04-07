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

def excel_a_base64():
    file_path = os.path.join(os.path.dirname(__file__), "attachment", "Formato_validacion.xlsx")

    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def enviar_correo(request: ReqMail, mensaje_html: str, correos: list[str]):
    destinatario = [request.emailUser]

    # Eliminar duplicados con el set y agregamos correo del usuario logueado
    correos_totales = list(set(correos + destinatario))
    print(f"--> CorreosTotales: {correos_totales}")
    
    tipo_solicitud = "Cliente" if request.isNew else "Actualización"
    subject = f"{tipo_solicitud}: {request.cliente} {request.rfc}"

    firma_b64 = fillFirma()
    # Armar payload
    data = {
        "sender": {
            "email": "web.app.no.reply@konnect.mx",
            "name": "Konnect"
        },
        "replyTo": {
            "email": request.emailUser
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
    

def enviar_correo_dispersion(cotizacion, mensaje_html, correos):
    logger.info("🚀 ENTRO A enviar_correo_dispersion")

    BREVO_API_KEY = os.getenv("BREVO_KEY")
    BREVO_URL = os.getenv("BREVO_LINK")

    if not BREVO_API_KEY:
        logger.error("❌ BREVO_KEY no configurada")
        return

    firma_b64 = fillFirma()
    excel_base64 = excel_a_base64()

    data = {
        "sender": {
            "email": "web.app.no.reply@konnect.mx",
            "name": "Konnect"
        },
        "to": [{"email": e} for e in correos],
        "subject": f"Dispersión Cotización {cotizacion.id_cotizacion} - {cotizacion.nombre} - {cotizacion.producto}",
        "htmlContent": mensaje_html,
        "attachment": [
            {
                "content": excel_base64,
                "name": "Formato_validacion.xlsx"
            },
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

    res = requests.post(BREVO_URL, json=data, headers=headers)
    print(f"Brevo response: ({res.status_code}) {res.text}")
    return "Correo enviado con éxito."

def enviar_correo_informativo(html_content: str, correos: list[str], subject: str, imagen_b64: str):
    headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }
    resultados = []

    data_base = {
        "sender": {
            "email": "web.app.no.reply@konnect.mx",
            "name": "Konnect"
        },
        "subject": subject,
        "htmlContent": html_content,
        "attachment": [
            {
                "name": "imagen_recordatorio.png",
                "content": imagen_b64,
                "contentId": "imagen_recordatorio"
            }
        ]
    }
    for mail in correos:
        try:
            data = data_base.copy() # Copiamos el objeto base para no mutarlo
            data["to"] = [{"email": mail}]

            res = requests.post(BREVO_URL, json=data, headers=headers,timeout=(3,10)) 
            # 3 Segundos para conectar, 10 para esperar respusta
            resultados.append({
                "email": mail,
                "status": res.status_code,
                "response": res.text
            })
        except  Exception as e:
            # ❗ Este correo falló, los demás siguen
            resultados.append({
                "email": mail,
                "ok": False,
                "error": str(e)
            })
            logger.error(f"emial: {mail}, error: {str(e)}")

    print(f"{resultados}")       
    return resultados

def enviar_correo_simple(html_content: str, correos: list[str], subject: str):

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    resultados = []

    data_base = {
        "sender": {
            "email": "web.app.no.reply@konnect.mx",
            "name": "Konnect"
        },
        "subject": subject,
        "htmlContent": html_content
    }

    for mail in correos:
        try:
            data = data_base.copy()
            data["to"] = [{"email": mail}]

            res = requests.post(BREVO_URL, json=data, headers=headers, timeout=(3,10))

            resultados.append({
                "email": mail,
                "status": res.status_code,
                "response": res.text
            })

        except Exception as e:
            resultados.append({
                "email": mail,
                "ok": False,
                "error": str(e)
            })

    print(resultados)
    return resultados

def send_mail_comment(request, correos, mensaje_html):
    try:
        logger.info("🚀 ENTRO A send_mail_comment")

        BREVO_API_KEY = os.getenv("BREVO_KEY")
        BREVO_URL = os.getenv("BREVO_LINK")

        if not BREVO_API_KEY:
            raise Exception("BREVO_KEY no configurada")

        firma_b64 = fillFirma()

        data = {
            "sender": {
                "email": "web.app.no.reply@konnect.mx",
                "name": "Konnect"
            },
            "to": [{"email": e} for e in correos],
            "subject": f"Mensaje de Dirección {request.id_cotizacion} - {request.cliente}",
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

        res = requests.post(BREVO_URL, json=data, headers=headers)

        if res.status_code >= 400:
            raise Exception(f"Error en Brevo: {res.text}")

        return {"ok": True, "message": "Correo enviado correctamente"}

    except Exception as e:
        logger.error(f"❌ Error enviando correo: {str(e)}")
        return {"ok": False, "error": str(e)}