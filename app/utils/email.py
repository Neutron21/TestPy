from email.mime.image import MIMEImage
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuración para Hostinger SMTP
SMTP_HOST = "smtp.hostinger.com"
SMTP_PORT = 587
SMTP_USER = "konecct.ti@solu-tec.net"
SMTP_PASSWORD = "Mexico_2025"
SMTP_FROM_NAME = "KONNECT"
SMTP_FROM_EMAIL = SMTP_USER

def enviar_correo(destinatario: str, mensaje: str):
    msg = MIMEMultipart("related")  # 👈 para permitir imágenes embebidas

    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg['To'] = destinatario
    msg['Subject'] = 'Correo de prueba desde Python'

    # Crear la parte HTML del mensaje
    msg_alternative = MIMEMultipart("alternative")
    msg.attach(msg_alternative)

    msg_alternative.attach(MIMEText(mensaje, 'html'))

    # Ruta corregida para la imagen de firma
    firma_path = os.path.join(os.path.dirname(__file__), "static", "firma.png")

    try:
        with open(firma_path, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<firma>')  # 👈 este ID debe coincidir con el usado en el HTML (cid:firma)
            img.add_header('Content-Disposition', 'inline', filename="firma.png")
            msg.attach(img)
    except FileNotFoundError:
        return f"Error: No se encontró la imagen de firma en {firma_path}"

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM_EMAIL, [destinatario], msg.as_string())
        server.quit()
        return "Correo enviado con éxito."
    except Exception as e:
        return f"Error al enviar el correo: {str(e)}"
