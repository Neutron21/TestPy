from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select, text
from app.db import SessionDep
from app.models import Comentarios, ComentariosDTO, Cotizacion, MontoUpdateDTO, Usuarios
from sqlmodel import desc

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
    try:
        user = session.get(Usuarios, id_usuario)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        

        if user.rol == 'if' or user.nivel >= 2  :
            query = select(Comentarios).where(
                Comentarios.id_cotizacion == id_cotizacion,
                Comentarios.visible == True)
        else:
            query = select(Comentarios).where(
                Comentarios.id_cotizacion == id_cotizacion,
                Comentarios.id_usuario != "gerencia.corporativa@konnect.mx",
                Comentarios.visible == True
            )
        
        comentarios = session.exec(query).all()
        return comentarios 

    except Exception as e:
        print(f"ERROR DETALLADO EN /comentarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/comentario", response_model=Comentarios) 
async def create_new_coment(coment_request: ComentariosDTO, session: SessionDep):
    coment_data = Comentarios(**coment_request.model_dump(exclude_unset=True))  
    session.add(coment_data)  
    session.commit() 
    session.refresh(coment_data) 
    return coment_data  


def soft_delete_comentario_logic(session, id_usuario: int, id_comentario: int) -> Comentarios:
    # 1. Consultamos al usuario para verificar su rol e ID
    user = session.get(Usuarios, id_usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Bloqueamos si el rol es 'if' o si su ID no está en la lista permitida
    if user.rol == "if" or id_usuario not in ALLOWED_COMMENT_DELETE_USERS:
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
    # Consultamos al usuario que hace la petición
    user = session.get(Usuarios, request.id_usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validamos que no sea rol 'if' y que esté en los permitidos
    if user.rol == "if" or request.id_usuario not in ALLOWED_COMMENT_DELETE_USERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los usuarios IF no tienen permitido borrar comentarios"
        )

    comentario = session.get(Comentarios, request.id_comentario)
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    
    comentario.visible = False
    session.add(comentario)
    session.commit()
    session.refresh(comentario)
    return comentario