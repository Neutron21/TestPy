from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import base64

router = APIRouter(tags=["Utils"])

class NumerosRequest(BaseModel):
    numeros: List[int]

def numeros_a_base64(lista_numeros):
    resultado = []
    for num in lista_numeros:
        numBytes = str(num).encode('utf-8')
        base64_bytes = base64.b64encode(numBytes)
        cotizacionB64 = base64_bytes.decode('utf-8')
        resultado.append(cotizacionB64)
    return resultado

@router.post("/utils", response_model=List[str])
async def get_base64_from_numeros(payload: NumerosRequest):
    return numeros_a_base64(payload.numeros)
