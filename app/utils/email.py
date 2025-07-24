from email.mime.image import MIMEImage
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.models import ReqMail

# Configuración para Hostinger SMTP
SMTP_HOST = "smtp.hostinger.com"
SMTP_PORT = 587
SMTP_USER = "web.app.no.reply@konnect.mx"
SMTP_PASSWORD = "TiaCaquitas_007"
SMTP_FROM_NAME = "KONNECT"
SMTP_FROM_EMAIL = SMTP_USER

def enviar_correo(request: ReqMail, mensaje: str, correos: list[str]):
    destinatario = request.emailUser

    # Correos fijos de Team Konnect
    correos_fijos = ['kfigueroa@konnect.mx', 'ara.castro@konnect.mx', destinatario]

    # Eliminar duplicados y combinar con correos fijos
    correos_totales = list(set(correos + correos_fijos))
    print(f"--> CorreosTotales: {correos_totales}")
    print(f"--> correos_fijos: {", ".join(correos_fijos)}")
    msg = MIMEMultipart("related")  # 👈 para permitir imágenes embebidas

    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg['To'] = ", ".join(correos_fijos)
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

        # todos_destinatarios = [destinatario] + correos
        server.sendmail(SMTP_FROM_EMAIL, correos_totales, msg.as_string())

        server.quit()
        return "Correo enviado con éxito."
    except Exception as e:
        return f"Error al enviar el correo: {str(e)}"
