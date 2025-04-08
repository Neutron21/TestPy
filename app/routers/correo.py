# routers/correo.py

from fastapi import APIRouter
from utils.email import enviar_correo  # Importa la función de enviar correo desde utils

router = APIRouter(tags=["Correo"])

@router.post("/enviar-correo")
async def enviar_mail():
    destinatario = "victor.hugo.silva01@gmail.com"  # O cualquier otro correo al que desees enviar
    mensaje = "Este es un mensaje de prueba enviado desde FastAPI."
    resultado = enviar_correo(destinatario, mensaje)  # Llamamos a la función para enviar el correo
    return {"mensaje": resultado}  # Retornamos el resultado (exitoso o error)
