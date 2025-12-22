from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
import os

from app.db import SessionDep
from app.models import Cotizacion

router = APIRouter(tags=["Borrar"])

@router.post("/cotizaciones/borrar-pruebas")
def borrar(request: Request, session: SessionDep):
    token = request.headers.get("X-Cron-Token")

    if not token:
        raise HTTPException(status_code=400, detail="Token requerido")

    if token != os.getenv("CRON_SECRET"):
        raise HTTPException(status_code=401, detail="Token inválido")

    total_borradas = (
        session.query(Cotizacion)
        .filter(func.lower(Cotizacion.nombre).like('%prueba%'))
        .delete(synchronize_session=False)
    )

    session.commit()

    return {
        "mensaje": "Cotizaciones de prueba borradas correctamente",
        "total_borradas": total_borradas
    }
