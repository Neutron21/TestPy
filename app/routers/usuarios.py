from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, text
from app.db import SessionDep
from app.models import UsuarioDTO, UsuarioResponse, UsuarioSimple, Usuarios

router = APIRouter(tags=["Usuarios"])



@router.get("/usuarioByMail", response_model=Usuarios)
async def usuario_by_mail(email: str, session: SessionDep):
    query = select(Usuarios).where(Usuarios.email == email)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no existe")
    print(user)
    return user


# -------------------------------------------------------------
# ✔ create_usuario (solo mejoras mínimas añadidas)
# -------------------------------------------------------------
@router.post("/usuarios", response_model=Usuarios)
async def create_usuario(usuario_data: UsuarioDTO, session: SessionDep):

    # <<< agregado: validar email único
    existing = session.exec(select(Usuarios).where(Usuarios.email == usuario_data.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya existe")

    # <<< agregado: normalizar campos 0 → None
    usuario_dict = usuario_data.model_dump()
    for field in ("id_financiera", "id_superior"):
        value = usuario_dict.get(field)
        if value in [0, "0", "", "null", None]:
            usuario_dict[field] = None

    usuario = Usuarios.model_validate(usuario_dict)  # (ESTO ya lo tenías)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario  


@router.get("/usuarios", response_model=List[UsuarioResponse])
async def get_usuarios(session: SessionDep):
    query = select(Usuarios).order_by(Usuarios.nombre)
    usuarios = session.exec(query).all()
    return usuarios


# -------------------------------------------------------------
# ✔ subordinados (solo el fix mínimo para devolver lista válida)
# -------------------------------------------------------------
@router.get("/usuarios/subordinados", response_model=list[UsuarioSimple])
async def list_brokers(id_user: int, session: SessionDep):
    queryUser = select(Usuarios).where(Usuarios.id == id_user)
    user = session.exec(queryUser).first()
    print(user)
    if user.rol == 'a':
        query = select(Usuarios.id, Usuarios.nombre)
        rows = session.exec(query).all()
        # <<< agregado: convertir a dict
        return [{"id": r.id, "nombre": r.nombre} for r in rows]

    else: 
        query = text("""
            WITH RECURSIVE subordinates AS (
                SELECT id, id_superior FROM usuarios WHERE id = :user_id
                UNION ALL
                SELECT u.id, u.id_superior
                FROM usuarios u
                INNER JOIN subordinates s ON u.id_superior = s.id
            )
            SELECT id, nombre, id_superior FROM usuarios WHERE id IN (SELECT id FROM subordinates)
            ORDER BY nombre         
            """)

    # <<< agregado: ejecutar + convertir resultado a lista JSON válida
    result = session.execute(query, {"user_id": id_user}).all()
    return [{"id": r[0], "nombre": r[1], "id_superior": r[2]} for r in result]


@router.get("/usuarios/superiores", response_model=list[UsuarioSimple])
async def get_usuarios_superiores(session: SessionDep):
    query = select(Usuarios.id, Usuarios.nombre, Usuarios.id_superior).where(
        Usuarios.id_superior.is_not(None),
        Usuarios.id_superior != 0
    )
    usuarios = session.exec(query).all()
    return [{"id": u.id, "nombre": u.nombre, "id_superior": u.id_superior} for u in usuarios]
