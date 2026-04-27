from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select, text
from app.db import SessionDep
from app.models import Comentarios, ComentariosDTO, Cotizacion, MontoUpdateDTO, Usuarios

router = APIRouter(tags=["Comentarios"])

@router.get("/comentarios/{id_cotizacion}/{id_usuario}", response_model=list[Comentarios])
async def obtener_comentarios(
    id_cotizacion: int, 
    id_usuario: int,
    session: SessionDep
):
    # Consultar el usuario
    user = session.get(Usuarios, id_usuario)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Si es nivel 2, regresar todos los comentarios
    if user.nivel >= 2:
        query = select(Comentarios).where(Comentarios.id_cotizacion == id_cotizacion)
        comentarios = session.exec(query).all()
        return comentarios
    
    # Si es nivel 1, excluir comentarios de "gerencia.corporativa@konnect.mx"
    else:
        query = select(Comentarios).where(
            Comentarios.id_cotizacion == id_cotizacion,
            Comentarios.id_usuario != "gerencia.corporativa@konnect.mx"
        )

    
    comentarios = session.exec(query).all()
    print(f"comentarios: {comentarios}")
    return comentarios 

@router.post("/comentario", response_model=Comentarios) 
async def create_new_coment(coment_request: ComentariosDTO, session: SessionDep):
    coment_data = Comentarios(**coment_request.model_dump(exclude_unset=True))  # exclude_unset=True previen inyeccion de campos NO definidos
    session.add(coment_data)  
    session.commit() 
    session.refresh(coment_data) 
    return coment_data  
    


