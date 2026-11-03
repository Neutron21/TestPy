import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

# Asegurarte de que exista la carpeta logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "konnect_api.log"

logger = logging.getLogger("konnect_api")
logger.setLevel(logging.INFO)
logger.propagate = False

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)


class BrevoAlertHandler(logging.Handler):
    def __init__(self, level=logging.CRITICAL):
        super().__init__(level)

    def emit(self, record):
        if record.levelno < logging.CRITICAL:
            return

        try:
            from app.utils.email import enviar_correo_alerta

            message = self.format(record)
            if record.exc_info:
                message = f"{message}\n\n{self.formatException(record.exc_info)}"

            enviar_correo_alerta(
                mensaje=message,
                asunto=f"Alerta de logs: {record.levelname}",
                log_path=str(LOG_FILE),
            )
        except Exception:
            # No detener el flujo normal del logging si falla el correo
            pass


alert_handler = BrevoAlertHandler()
alert_handler.setFormatter(formatter)
alert_handler.setLevel(logging.CRITICAL)

if not logger.handlers:  # Evita duplicar handlers si se importa varias veces
    logger.addHandler(file_handler)
    logger.addHandler(alert_handler)
