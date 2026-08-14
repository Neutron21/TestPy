from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select, text
from app.db import SessionDep
from app.models import Comentarios, ComentariosDTO, Cotizacion, MontoUpdateDTO, Usuarios
from sqlmodel import desc # Importa esto


router = APIRouter(tags=["Comentarios"])

ALLOWED_COMMENT_DELETE_USERS = {1, 2, 9, 14, 15, 23, 42, 43}


class DeleteComentarioRequest(BaseModel):
    id_usuario: int
    id_comentario: int


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
        query = select(Comentarios).where(
            Comentarios.id_cotizacion == id_cotizacion,
            Comentarios.visible == True)
        comentarios = session.exec(query).all()
        return comentarios
    
    # Si es nivel 1, excluir comentarios de "gerencia.corporativa@konnect.mx"
    else:
        query = select(Comentarios).where(
            Comentarios.id_cotizacion == id_cotizacion,
            Comentarios.id_usuario != "gerencia.corporativa@konnect.mx",
            Comentarios.visible == True
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
    

@router.get("/ultimo-comentario/{id_cotizacion}/{id_usuario}")
async def obtener_ultimo_comentario(
    id_cotizacion: int, 
    id_usuario: int,
    session: SessionDep
):
    user = session.get(Usuarios, id_usuario)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    query = select(Comentarios).where(Comentarios.id_cotizacion == id_cotizacion)
    
    if user.nivel < 2:
        query = query.where(Comentarios.id_usuario != "gerencia.corporativa@konnect.mx")
    
    query = query.order_by(desc(Comentarios.id)).limit(1)
    
    comentario = session.exec(query).first()
    
    return comentario if comentario else {"comentarios": "Sin comentarios"}

def soft_delete_comentario_logic(session, id_usuario: int, id_comentario: int) -> Comentarios:
    if id_usuario not in ALLOWED_COMMENT_DELETE_USERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no autorizado para borrar comentarios"
        )

    comentario = session.get(Comentarios, id_comentario)
    if not comentario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado"
        )

    if not comentario.visible:
        return comentario

    comentario.visible = False
    session.add(comentario)
    session.commit()
    session.refresh(comentario)
    return comentario


@router.patch("/comentario-delete", response_model=Comentarios)
async def delete_comentario(
    request: DeleteComentarioRequest,
    session: SessionDep,
):
    comentario = session.get(Comentarios, request.id_comentario)
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    
    comentario.visible = False
    session.add(comentario)
    session.commit()
    session.refresh(comentario)
    return comentario