from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import base64
import os
import shutil
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

router = APIRouter(tags=["Utils"])

# ---------- MODELOS ----------
class NumerosRequest(BaseModel):
    numeros: List[int]

class DeleteRequest(BaseModel):
    folder_b64: str   # nombre de la carpeta codificado en base64

# ---------- UTILIDADES ----------
def numeros_a_base64(lista_numeros):
    resultado = []
    for num in lista_numeros:
        numBytes = str(num).encode('utf-8')
        base64_bytes = base64.b64encode(numBytes)
        cotizacionB64 = base64_bytes.decode('utf-8')
        resultado.append(cotizacionB64)
    return resultado

# ---------- ENDPOINTS ----------
# @router.post("/utils", response_model=List[str])
# async def get_base64_from_numeros(payload: NumerosRequest):
#     arrayB64 = numeros_a_base64(payload.numeros)
#     for numB64 in arrayB64:
#         try:
#             # Decodificar base64 → nombre real de la carpeta
#             # folder_name = base64.b64decode(payload.folder_b64).decode("utf-8")
#             folder_name = numB64

#             # Obtener ruta desde .env
#             base_path = os.getenv("RUTA_COTIZACIONES")
#             if not base_path:
#                 return {"status": "error", "message": "RUTA_COTIZACIONES no está definida en .env"}

#             # Construir ruta completa
#             folder_path = os.path.join(base_path, folder_name)

#             if os.path.exists(folder_path):
#                 shutil.rmtree(folder_path)  # elimina toda la carpeta
#                 print({f"OK, Carpeta '{folder_name}' eliminada de cotizaciones"})
#             else:
#                 print({f"Error, Carpeta '{folder_name}' no encontrada en cotizaciones"})

#         except Exception as e:
#             return {"status": "error", "message": str(e)}

#     return numeros_a_base64(payload.numeros)


# @router.delete("/delete-cotizacion")
async def delete_cotizacion(payload: DeleteRequest):
    """
    Borra una carpeta dentro de la ruta RUTA_COTIZACIONES,
    a partir de su nombre en base64.
    """

    try:
        # Decodificar base64 → nombre real de la carpeta
        # folder_name = base64.b64decode(payload.folder_b64).decode("utf-8")
        folder_name = payload.folder_b64

        # Obtener ruta desde .env
        base_path = os.getenv("RUTA_COTIZACIONES")
        if not base_path:
            return {"status": "error", "message": "RUTA_COTIZACIONES no está definida en .env"}

        # Construir ruta completa
        folder_path = os.path.join(base_path, folder_name)

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)  # elimina toda la carpeta
            return {"status": "ok", "message": f"Carpeta '{folder_name}' eliminada de cotizaciones"}
        else:
            return {"status": "error", "message": f"Carpeta '{folder_name}' no encontrada en cotizaciones"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
