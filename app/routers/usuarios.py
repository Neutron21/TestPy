from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, text
from app.db import SessionDep
from app.models import (
    UsuarioDTO,
    UsuarioResponse,
    UsuarioSimple,
    Usuarios
)

router = APIRouter(tags=["Usuarios"])


# ============================================================
# Obtener usuario por email → SOLO id y nombre
# ============================================================
@router.get(
    "/usuarioByMail",
    response_model=Usuarios
)
async def usuario_by_mail(email: str, session: SessionDep):
    user = session.exec(
        select(Usuarios).where(Usuarios.email == email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no existe"
        )

    return user



# ============================================================
# Crear usuario → responde SOLO id y nombre
# ============================================================
@router.post(
    "/usuarios",
    response_model=UsuarioSimple
)
async def create_usuario(usuario_data: UsuarioDTO, session: SessionDep):

    existing = session.exec(
        select(Usuarios).where(Usuarios.email == usuario_data.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya existe"
        )

    usuario_dict = usuario_data.model_dump()

    for field in ("id_financiera", "id_superior"):
        if usuario_dict.get(field) in [0, "0", "", "null", None]:
            usuario_dict[field] = None

    usuario = Usuarios.model_validate(usuario_dict)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return {"id": usuario.id, "nombre": usuario.nombre}


# ============================================================
# Listar usuarios → SOLO id y nombre (para los que ya existen)
# ============================================================
@router.get(
    "/usuarios",
    response_model=List[UsuarioSimple]
)
async def get_usuarios(session: SessionDep):
    rows = session.exec(
        select(Usuarios.id, Usuarios.nombre)
        .order_by(Usuarios.nombre)
    ).all()

    return [{"id": r.id, "nombre": r.nombre} for r in rows]


# ============================================================
# Subordinados
# ============================================================
@router.get(
    "/usuarios/subordinados",
    response_model=List[UsuarioSimple]
)
async def list_brokers(id_user: int, session: SessionDep):

    user = session.exec(
        select(Usuarios).where(Usuarios.id == id_user)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no existe"
        )

    # Admin → todos
    if user.rol == 'a':
        rows = session.exec(
            select(Usuarios.id, Usuarios.nombre)
        ).all()

        return [{"id": r.id, "nombre": r.nombre} for r in rows]

    # No admin → jerarquía
    query = text("""
        WITH RECURSIVE subordinates AS (
            SELECT id, id_superior FROM usuarios WHERE id = :user_id
            UNION ALL
            SELECT u.id, u.id_superior
            FROM usuarios u
            INNER JOIN subordinates s ON u.id_superior = s.id
        )
        SELECT id, nombre FROM usuarios
        WHERE id IN (SELECT id FROM subordinates)
        ORDER BY nombre
    """)

    result = session.execute(query, {"user_id": id_user}).all()
    return [{"id": r[0], "nombre": r[1]} for r in result]


# ============================================================
# Superiores → SOLO id y nombre
# ============================================================
@router.get(
    "/usuarios/superiores",
    response_model=List[UsuarioSimple]
)
async def get_usuarios_superiores(session: SessionDep):
    rows = session.exec(
        select(Usuarios.id, Usuarios.nombre)
        .where(
            Usuarios.id_superior.is_not(None),
            Usuarios.id_superior != 0
        )
    ).all()

    return [{"id": r.id, "nombre": r.nombre} for r in rows]


