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

@router.patch("/comentarios/actualizar_monto", response_model=Cotizacion)
async def actualizar_monto_y_comentar(data: MontoUpdateDTO, session: SessionDep):
    print(f"➡️ PATCH recibido: {data}")
    
    cotizacion = session.get(Cotizacion, data.id_cotizacion)
    print(f"🔍 Cotización encontrada: {cotizacion}")

    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    monto_anterior = cotizacion.monto
    print(f"💰 Monto anterior: {monto_anterior}")

    cotizacion.monto = data.monto
    session.add(cotizacion)

    texto = f"Se cambió el monto de ${monto_anterior:,.2f} a ${data.monto:,.2f}"
    comentario = Comentarios(
        id_cotizacion=data.id_cotizacion,
        comentarios=texto
    )
    session.add(comentario)

    session.commit()
    session.refresh(cotizacion)
    print("✅ Monto actualizado y comentario guardado")

    return cotizacion
