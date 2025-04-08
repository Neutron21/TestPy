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
    msg = MIMEMultipart()
    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg['To'] = destinatario
    msg['Subject'] = 'Correo de prueba desde Python'

    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return "Correo enviado con éxito."
    except Exception as e:
        return f"Error al enviar el correo: {str(e)}"
