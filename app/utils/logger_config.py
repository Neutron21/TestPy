import logging
from logging.handlers import RotatingFileHandler
import os

# Asegurarte de que exista la carpeta logs
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("konnect_api")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "logs/konnect_api.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)

if not logger.handlers:  # Evita duplicar handlers si se importa varias veces
    logger.addHandler(handler)
