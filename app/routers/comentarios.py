from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Comentarios

router = APIRouter(tags=["Comentarios"])

@router.get("/comentarios/{id_cotizacion}")
async def obtener_comentarios(id_cotizacion: int, session: SessionDep):
    query = select(Comentarios).where(Comentarios.id_cotizacion == id_cotizacion)
    comentarios = session.exec(query).all()  # Obtener todos los resultados

    if not comentarios:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay comentarios para esta cotización")
    
    if len(comentarios) == 1:
        return comentarios[0]
    
    return comentarios 
@router.get("/comentarios/usuario/{id_usuario}")
async def obtener_comentarios_por_usuario(id_usuario: str, session: SessionDep):
    query = select(Comentarios).where(Comentarios.id_usuario == id_usuario)
    comentarios = session.exec(query).all()  

    if not comentarios:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay comentarios para este usuario")
    
    if len(comentarios) == 1:
        return comentarios[0]
    
    return comentarios 

