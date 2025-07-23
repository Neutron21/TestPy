from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import and_
from sqlmodel import select

from app.models import Tp_producto_checklist, ChecklistResponse, Productos
from app.db import SessionDep


router = APIRouter(tags=["Checklist"])

@router.get("/checklist", response_model=ChecklistResponse)
async def obtener_checklist(
    session: SessionDep,
    producto_id: int = Query(...),
    tipo_persona: str = Query(...)):

    stmt = (
        select(
            Tp_producto_checklist.producto_id,
            Tp_producto_checklist.tipo_persona,
            Tp_producto_checklist.checklist,
            Tp_producto_checklist.ch_viabilidad,
            Productos.id_categoria,
            Productos.id_subCategoria
        )
        .join(Productos, Productos.id == Tp_producto_checklist.producto_id)
        .where(
            and_(
                Tp_producto_checklist.producto_id == producto_id,
                Tp_producto_checklist.tipo_persona == tipo_persona
            )
        )
    )

    result = session.exec(stmt).first()

    if not result:
        raise HTTPException(status_code=404, detail="Checklist no encontrado")

    # Empaqueta el resultado en el modelo de respuesta
    return ChecklistResponse(
        producto_id=result.producto_id,
        tipo_persona=result.tipo_persona,
        checklist=result.checklist,
        ch_viabilidad=result.ch_viabilidad,
        id_categoria=result.id_categoria,
        id_subCategoria=result.id_subCategoria
    )