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

def enviar_correo(request: ReqMail, mensaje: str, correos: list[str]):
    destinatario = [request.emailUser]

    # Eliminar duplicados con el set y agregamos correo del usuario logueado
    correos_totales = list(set(correos + destinatario))
    print(f"--> CorreosTotales: {correos_totales}")
    
    msg = MIMEMultipart("related")  # 👈 para permitir imágenes embebidas

    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg['To'] = ", ".join(destinatario)
    msg['Cc'] = ", ".join(correos)
    msg['Reply-To'] = "Konnect <kfigueroa@konecct.com.mx>"
    tipo_solicitud = "Cliente" if request.isNew else "Actualización"
    msg['Subject'] = f"{tipo_solicitud}: {request.cliente} {request.rfc}"

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

        # server.sendmail(SMTP_FROM_EMAIL, correos_totales, msg.as_string())
        for destino in correos_totales:
            print(f"Enviando a {destino}")
            server.sendmail(SMTP_FROM_EMAIL, destino, msg.as_string())
            time.sleep(9)  # Evitar rate limit de Hostinger

        server.quit()
        return "Correo enviado con éxito."
    except Exception as e:
        logger.error(f"Request: {request}")
        logger.error(f"❌ Error al enviar el correo FN(enviar_correo): {str(e)}")
        return f"Error al enviar el correo: {str(e)}"

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