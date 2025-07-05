from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db import SessionDep
from app.models import Comentarios, ComentariosDTO, Cotizacion, MontoUpdateDTO

router = APIRouter(tags=["Comentarios"])

@router.get("/comentarios/{id_cotizacion}", response_model=list[Comentarios])
async def obtener_comentarios(id_cotizacion: int, session: SessionDep):
    query = select(Comentarios).where(Comentarios.id_cotizacion == id_cotizacion)
    comentarios = session.exec(query).all() 
    print(f"comentarios: {comentarios}")
    # if not comentarios:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay comentarios para esta cotización")
    return comentarios 

@router.post("/comentario", response_model=Comentarios) 
async def create_new_coment(coment_request: ComentariosDTO, session: SessionDep):
    coment_data = Comentarios(**coment_request.model_dump(exclude_unset=True))  # exclude_unset=True previen inyeccion de campos NO definidos
    session.add(coment_data)  
    session.commit() 
    session.refresh(coment_data) 
    return coment_data  
