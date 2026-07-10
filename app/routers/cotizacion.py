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

@router.get("/cotizaciones") # Quitamos response_model temporalmente si da error
async def obtener_cotizaciones_por_usuario(
    session: SessionDep,
    id_user: Optional[int] = Query(None),
    nivel_user: Optional[int] = Query(None)):

    # Agregamos el JOIN en todas las consultas manuales
    join_sql = """
        LEFT JOIN (
            SELECT id_cotizacion, MAX(timestamp) AS ultimo_comentario
            FROM comentarios GROUP BY id_cotizacion
        ) uc ON c.id_cotizacion = uc.id_cotizacion
    """

    if nivel_user == 4:
        query = text(f"SELECT c.*, uc.ultimo_comentario FROM cotizacion c {join_sql} ORDER BY c.timestamp DESC")
        result = session.execute(query)
    elif nivel_user in [2, 3]:
        query = text(f"""
            WITH RECURSIVE subordinates AS (
              SELECT id FROM usuarios WHERE id = :user_id
              UNION ALL
              SELECT u.id FROM usuarios u
              INNER JOIN subordinates s ON u.id_superior = s.id
            )
            SELECT c.*, uc.ultimo_comentario FROM cotizacion c {join_sql}
            WHERE c.id_user IN (SELECT id FROM subordinates)
            ORDER BY c.timestamp DESC
        """)
        result = session.execute(query, {"user_id": id_user})
    else:
        query = text(f"SELECT c.*, uc.ultimo_comentario FROM cotizacion c {join_sql} WHERE c.id_user = :id_user ORDER BY c.timestamp DESC")
        result = session.execute(query, {"id_user": id_user})
    
    # IMPORTANTE: Devolvemos diccionarios, no objetos Cotizacion
    return [dict(row._mapping) for row in result.fetchall()]

@router.get("/cotizacion/buscar/", response_model=List[Cotizacion])
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
    rows = [] 
    
    if estatus is None and fin is None and not folioUserRfc and not fechaDesde and not fechaHasta and not broker and not idUser:
        raise HTTPException(status_code=400, detail="Error: Campos incompletos.")

    query_filters = ""
    params = {}

    if estatus is not None:
        query_filters += " AND estatus = :estatus"
        params["estatus"] = estatus

    if fin is not None:
        query_filters += " AND id_financiera = :fin"
        params["fin"] = fin

    if broker is not None:
        query_filters += " AND broker = :broker"
        params["broker"] = broker
    
    if idUser is not None:
        query_filters += " AND id_user = :idUser"
        params["idUser"] = idUser

    if fechaDesde and fechaHasta:
        query_filters += " AND timestamp BETWEEN :fechaDesde AND :fechaHasta"
        params["fechaDesde"] = fechaDesde
        params["fechaHasta"] = fechaHasta + " 23:59:59"

    if folioUserRfc:
        like = f"%{folioUserRfc}%"
        if rol == 'a':
            query_filters += " AND (id_usuario LIKE :like OR nombre LIKE :like OR rfc LIKE :like OR id_cotizacion = :folioUserRfc)"
        else:
            query_filters += " AND (nombre LIKE :like OR rfc LIKE :like OR id_cotizacion = :folioUserRfc)"
        params["like"] = like
        params["folioUserRfc"] = folioUserRfc

    # Aquí decides si usas recursive o no
    if rol != 'a' and user:
        query = f"""
        WITH RECURSIVE subordinates AS (
            SELECT id FROM usuarios WHERE id = :user_id
            UNION ALL
            SELECT u.id FROM usuarios u
            JOIN subordinates s ON u.id_superior = s.id
        )
        SELECT * FROM cotizacion
        WHERE id_user IN (SELECT id FROM subordinates)
        {query_filters}
        ORDER BY timestamp DESC
        """
        params["user_id"] = user
    else:
        query = f"""
        SELECT * FROM cotizacion
        WHERE 1=1
        {query_filters}
        ORDER BY timestamp DESC
        """

    print(f"QUERY: {query}")
    print(f"PARAMS: {params}")
    result = session.execute(text(query), params)

    rows = [Cotizacion(**row._mapping) for row in result]
    print(f"Total rows: {len(rows)}")
    print(f"Contenido: {rows}")
   
    return rows

@router.get("/cotizacion/byFin/{id_financiera}" , response_model=List[Cotizacion])
async def get_cotizacion_by_id(id_financiera: int, session: SessionDep):
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
async def update_estatus_cotizacion(
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
