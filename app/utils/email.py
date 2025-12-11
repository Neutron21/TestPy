import base64
import requests
from email.mime.image import MIMEImage
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from app.utils.logger_config import logger
from app.models import ReqMail

# Configuración para Hostinger SMTP
SMTP_HOST = "smtp.hostinger.com"
SMTP_PORT = 587
SMTP_USER = "web.app.no.reply@konnect.mx"
SMTP_PASSWORD = "TiaCaquitas_007"
SMTP_FROM_NAME = "KONNECT"
SMTP_FROM_EMAIL = SMTP_USER
BREVO_API_KEY = os.getenv("BREVO_KEY") 
BREVO_URL = os.getenv("BREVO_LINK")

def enviar_correo(request: ReqMail, mensaje_html: str, correos: list[str]):
    destinatario = [request.emailUser]

    # Eliminar duplicados con el set y agregamos correo del usuario logueado
    correos_totales = list(set(correos + destinatario))
    print(f"--> CorreosTotales: {correos_totales}")
    
    tipo_solicitud = "Cliente" if request.isNew else "Actualización"
    subject = f"{tipo_solicitud}: {request.cliente} {request.rfc}"
    # Cargar firma (inline)
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
    }
    # Adjuntar firma inline
    if firma_b64:
        data["inlineImages"] = [{
            "name": "firma.png",
            "content": firma_b64
        }]

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    try:
        res = requests.post(BREVO_URL, json=data, headers=headers)
        logger.info(f"Brevo response: ({res.status_code}) {res.text}")
    except Exception as e:
        logger.error(f"Request: {data}")
        logger.error(f"❌ Error al enviar el correo: {str(e)}")

def notificacion_if(cliente: str, mensaje: str, correos: list[str]):

    
    msg = MIMEMultipart("related")  # 👈 para permitir imágenes embebidas

    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg['To'] = ", ".join(correos)
    # msg['Cc'] = ", ".join(correos)
    # msg['Reply-To'] = "Konnect <kfigueroa@konecct.com.mx>"
    
    msg['Subject'] = f"La IF comento sobre el cliente {cliente}"

    # Crear la parte HTML del mensaje
    msg_alternative = MIMEMultipart("alternative")
    msg.attach(msg_alternative)

    msg_alternative.attach(MIMEText(mensaje, 'html'))

    firma_path = os.path.join(os.path.dirname(__file__), "static", "firma.png")

    try:
        with open(firma_path, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<firma>')
            img.add_header('Content-Disposition', 'inline', filename="firma.png")
            msg.attach(img)
    except FileNotFoundError:
        return f"Error: No se encontró la imagen de firma en {firma_path}"

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)

        server.sendmail(SMTP_FROM_EMAIL, correos, msg.as_string())

        server.quit()
        return "Correo enviado con éxito."
    except Exception as e:
        logger.error(f"Request: {cliente} -- {mensaje}")
        logger.error(f"❌ Error al enviar el correo FN(notificacion_if): {str(e)}")
        return f"Error al enviar el correo: {str(e)}"