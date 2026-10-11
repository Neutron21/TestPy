from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, text
from app.db import SessionDep
from app.models import (
    UsuarioDTO,
    UsuarioResponse,
    UsuarioSimple,
    UsuarioUpdate,
    Usuarios
)
from datetime import datetime, timedelta
from fastapi import BackgroundTasks

from app.routers.send_mail import enviar_correo_solicitud_utms


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

# Crear usuario →

@router.post(
    "/usuarios",
    response_model=Usuarios
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

    # 🔥 CAMBIO IMPORTANTE
    usuario = Usuarios(
        **usuario_dict,
        comisiones="evoluciona"
    )

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

# ============================================================
# Status de Usuarios 
# ============================================================
@router.get("/usuarios/payment-status")
async def payment_status(id_user: int, session: SessionDep):

    user = session.exec(
        select(Usuarios).where(Usuarios.id == id_user)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no existe")
    
    if user.id_financiera:
       return {
        "status": "active"
        }

    if not user.f_ultimo_pago:
        return {
            "status": "no_payment"
        }

    # 👇 TODO como DATE
    hoy = datetime.now().date()
    ultimo_pago = user.f_ultimo_pago

    fecha_vencimiento = ultimo_pago.replace(year=ultimo_pago.year + 1)
    fecha_aviso = fecha_vencimiento - timedelta(days=30)

    # 🔴 VENCIDO
    if hoy >= fecha_vencimiento:
        return {
            "status": "expired",
            "fecha_vencimiento": fecha_vencimiento
        }

    # 🟡 WARNING
    if hoy >= fecha_aviso:
        dias_restantes = (fecha_vencimiento - hoy).days

        return {
            "status": "warning",
            "fecha_vencimiento": fecha_vencimiento,
            "dias_restantes": dias_restantes
        }

    # 🟢 ACTIVO
    return {
        "status": "active"
    }
# ============================================================
# Pedir UMTs Usuario Nuevo/Existente
# ============================================================
@router.post("/usuarios/{id_usuario}/notificar-utms-faltantes")
async def notificar_utms_faltantes(
    id_usuario: int, 
    session: SessionDep, 
    background_tasks: BackgroundTasks
):
    user = session.exec(select(Usuarios).where(Usuarios.id == id_usuario)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no existe")

    # 1. Calcular financieras faltantes
    ids_base = (1, 4, 11, 12, 32, 37)
    query = text("""
        SELECT financieras.id, financieras.nombre 
        FROM financieras 
        WHERE financieras.id IN :ids_base
        AND financieras.id NOT IN (
            SELECT id_financiera FROM utms WHERE id_usuario = :id_usuario
        )
    """)
    faltantes = session.execute(query, {"ids_base": ids_base, "id_usuario": id_usuario}).mappings().all()
    if not faltantes:
        return {"ok": False, "mensaje": "El usuario ya cuenta con UTMs para todas las financieras."}

    ids_faltantes = [fin["id"] for fin in faltantes]

    # 2. Reutilizar la función de envío
    destinatarios = enviar_correo_solicitud_utms(
        user, ids_faltantes, "Solicitud de UTMs Faltantes", session, background_tasks
    )

    if not destinatarios:
        return {"ok": False, "mensaje": "No se encontraron correos para las financieras faltantes."}

    return {
        "ok": True,
        "mensaje": "Correo enviado correctamente",
        "instituciones_faltantes": list(faltantes),
        "destinatarios": destinatarios
    }

# ============================================================
# Actualizar usuario
# ============================================================
@router.patch(
    "/usuarios/{id_usuario}",
    response_model=Usuarios
)
async def update_usuario(
    id_usuario: int,
    usuario_data: UsuarioUpdate,
    session: SessionDep
):

    usuario = session.exec(
        select(Usuarios).where(Usuarios.id == id_usuario)
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no existe"
        )

    # Si se está modificando el correo, verificar que no exista otro usuario
    if usuario_data.email is not None and usuario_data.email != usuario.email:

        existing = session.exec(
            select(Usuarios).where(
                Usuarios.email == usuario_data.email,
                Usuarios.id != id_usuario
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya existe"
            )

    # Obtener solamente los campos que fueron enviados
    datos = usuario_data.model_dump(exclude_unset=True)

    # Actualizar usuario
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return usuario


