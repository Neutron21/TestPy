from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status, Path
from sqlalchemy import desc
from sqlmodel import select, text
from app.db import SessionDep
from app.models import Cotizacion, CotizacionDTO, EstatusUpdate, FechaPagoDTO, MontoUpdate
import base64
from sqlmodel import update
from datetime import date
from fastapi import APIRouter
from sqlmodel import select

from app.models import Cotizacion


from app.routers import comentarios

router = APIRouter(tags=["Cotizacion"])

@router.get("/cotizacion/{id_cotizacion}" , response_model=Cotizacion)
async def get_cotizacion_by_id(id_cotizacion: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cotizacion = session.exec(query).first()
    if not cotizacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe la Cotización")
    return  cotizacion

@router.get("/cotizaciones") 
async def obtener_cotizaciones_por_usuario(
    session: SessionDep,
    id_user: Optional[int] = Query(None),
    nivel_user: Optional[int] = Query(None)):

    join_sql = """
        LEFT JOIN (
            SELECT id_cotizacion, MAX(timestamp) AS max_timestamp
            FROM comentarios GROUP BY id_cotizacion
        ) last_c ON c.id_cotizacion = last_c.id_cotizacion
        LEFT JOIN comentarios uc ON uc.id_cotizacion = last_c.id_cotizacion 
        AND uc.timestamp = last_c.max_timestamp
    """

    if nivel_user == 4:
        query = text(f"SELECT c.*, uc.comentarios AS ultimo_comentario FROM cotizacion c {join_sql} ORDER BY c.timestamp DESC")
        result = session.execute(query)
    elif nivel_user in [2, 3]:
        query = text(f"""
            WITH RECURSIVE subordinates AS (
              SELECT id FROM usuarios WHERE id = :user_id
              UNION ALL
              SELECT u.id FROM usuarios u
              INNER JOIN subordinates s ON u.id_superior = s.id
            )
            SELECT c.*, uc.comentarios AS ultimo_comentario FROM cotizacion c {join_sql}
            WHERE c.id_user IN (SELECT id FROM subordinates)
            ORDER BY c.timestamp DESC
        """)
        result = session.execute(query, {"user_id": id_user})
    else:
        query = text(f"SELECT c.*, uc.comentarios AS ultimo_comentario FROM cotizacion c {join_sql} WHERE c.id_user = :id_user ORDER BY c.timestamp DESC")
        result = session.execute(query, {"id_user": id_user})
    
    return [dict(row._mapping) for row in result.fetchall()]

@router.get("/cotizacion/buscar/")
async def buscador_cotizaciones(
    session: SessionDep,
    estatus: Optional[int] = Query(None),
    fin: Optional[int] = Query(None),
    broker: Optional[int] = Query(None),
    idUser: Optional[int] = Query(None),
    folioUserRfc: Optional[str] = Query(None),
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    user: Optional[int] = Query(None),
    rol: Optional[str] = Query(None),
    ):
    
    if estatus is None and fin is None and not folioUserRfc and not fechaDesde and not fechaHasta and not broker and not idUser:
        raise HTTPException(status_code=400, detail="Error: Campos incompletos.")

    query_filters = ""
    params = {}
    alias_prefix = "c." # Usamos alias c. para todas las consultas del buscador para mantener consistencia
    
    # Definimos el join de comentarios para todas las consultas del buscador
    join_sql = """
        LEFT JOIN (
            SELECT id_cotizacion, MAX(timestamp) AS ultimo_comentario
            FROM comentarios
            GROUP BY id_cotizacion
        ) uc ON c.id_cotizacion = uc.id_cotizacion
    """

    if estatus is not None:
        query_filters += f" AND {alias_prefix}estatus = :estatus"
        params["estatus"] = estatus

    if fin is not None:
        query_filters += f" AND {alias_prefix}id_financiera = :fin"
        params["fin"] = fin

    if broker is not None:
        query_filters += f" AND {alias_prefix}broker = :broker"
        params["broker"] = broker
    
    if idUser is not None:
        query_filters += f" AND {alias_prefix}id_user = :idUser"
        params["idUser"] = idUser

    if fechaDesde and fechaHasta:
        query_filters += f" AND {alias_prefix}timestamp BETWEEN :fechaDesde AND :fechaHasta"
        params["fechaDesde"] = fechaDesde
        params["fechaHasta"] = fechaHasta + " 23:59:59"

    if folioUserRfc:
        like = f"%{folioUserRfc}%"
        if rol == 'a':
            query_filters += " AND (c.id_usuario LIKE :like OR c.nombre LIKE :like OR c.rfc LIKE :like OR c.id_cotizacion = :folioUserRfc)"
        else:
            query_filters += " AND (c.nombre LIKE :like OR c.rfc LIKE :like OR c.id_cotizacion = :folioUserRfc)"
        params["like"] = like
        params["folioUserRfc"] = folioUserRfc

    if rol != 'a' and user:
        query = f"""
        WITH RECURSIVE subordinates AS (
            SELECT id FROM usuarios WHERE id = :user_id
            UNION ALL
            SELECT u.id FROM usuarios u
            JOIN subordinates s ON u.id_superior = s.id
        )
        SELECT c.*, uc.ultimo_comentario FROM cotizacion c
        {join_sql}
        WHERE c.id_user IN (SELECT id FROM subordinates)
        {query_filters}
        ORDER BY c.timestamp DESC
        """
        params["user_id"] = user
    else:
        query = f"""
        SELECT c.*, uc.ultimo_comentario FROM cotizacion c
        {join_sql}
        WHERE 1=1
        {query_filters}
        ORDER BY c.timestamp DESC
        """

    print(f"QUERY: {query}")
    print(f"PARAMS: {params}")
    result = session.execute(text(query), params)

    # Devolvemos diccionarios con el mapeo correcto incluyendo el ultimo_comentario
    rows = [dict(row._mapping) for row in result]
    print(f"Total rows: {len(rows)}")
   
    return rows

@router.get("/cotizacion/byFin/{id_financiera}" , response_model=List[Cotizacion])
async def get_cotizacion_by_fin_endpoint(id_financiera: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_financiera == id_financiera).order_by(desc(Cotizacion.timestamp))
    cotizacion = session.exec(query).all()
    if not cotizacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe la Cotización")
    return  cotizacion

@router.post("/cotizacion", response_model=Cotizacion) 
async def create_cotizacion(usuario_data: CotizacionDTO, session: SessionDep):
    cotizacion = Cotizacion.model_validate(usuario_data.model_dump())  
    session.add(cotizacion)  
    session.commit() 
    session.refresh(cotizacion) 
    return cotizacion  

@router.patch("/cotizacion/status_udpate", response_model=Cotizacion)
async def update_estatus_cotizacion(
    estatus_data: EstatusUpdate, session: SessionDep,):

    cotizacion = session.get(Cotizacion, estatus_data.id_cotizacion)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    cotizacion.estatus = estatus_data.estatus
    session.add(cotizacion)
    session.commit()
    session.refresh(cotizacion)
    
    return cotizacion

@router.patch("/cotizacion/monto_udpate", response_model=Cotizacion)
async def update_monto_cotizacion(
    request: MontoUpdate, session: SessionDep,):

    cotizacion = session.get(Cotizacion, request.id_cotizacion)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    cotizacion.monto = request.monto
    session.add(cotizacion)
    session.commit()
    session.refresh(cotizacion)
    
    return cotizacion

@router.patch("/updatefechaPago")
async def update_fecha_pago(
    data: FechaPagoDTO,
    session: SessionDep
):
    try:
        session.expunge_all()
        statement = (
            update(Cotizacion)
            .where(Cotizacion.id_cotizacion == data.id_cotizacion)
            .values(fecha_pago=data.fecha_pago)
        )
        result = session.exec(statement)
        session.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")

        return {"ok": True, "mensaje": "Columna fecha_pago actualizada exitosamente"}

    except Exception as e:
        session.rollback()
        print(f"Error detectado: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error de integridad: el sistema intentó tocar la tabla comentarios"
        )