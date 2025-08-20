from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status, Path
from sqlalchemy import desc
from sqlmodel import select, text
from app.db import SessionDep
from app.models import Cotizacion, CotizacionDTO, EstatusUpdate, MontoUpdate
import base64

router = APIRouter(tags=["Cotizacion"])

@router.get("/cotizacion/{id_cotizacion}" , response_model=Cotizacion)
async def get_cotizacion_by_id(id_cotizacion: int, session: SessionDep):
    query = select(Cotizacion).where(Cotizacion.id_cotizacion == id_cotizacion)
    cotizacion = session.exec(query).first()
    if not cotizacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe la Cotización")
    return  cotizacion

@router.get("/cotizaciones", response_model=list[Cotizacion])
async def obtener_cotizaciones_por_usuario(
    session: SessionDep,
    id_user: Optional[int] = Query(None),
    nivel_user: Optional[int] = Query(None)):

    if nivel_user == 4:
        # MasterBroker ve todo
        cotizaciones = session.exec(select(Cotizacion).order_by(desc(Cotizacion.timestamp))).all()
    elif nivel_user in [2, 3]:
        # Director o Gerente ve las suyas y las de sus subordinados
        query = text("""
            WITH RECURSIVE subordinates AS (
              SELECT id FROM usuarios WHERE id = :user_id
              UNION ALL
              SELECT u.id FROM usuarios u
              INNER JOIN subordinates s ON u.id_superior = s.id
            )
            SELECT * FROM cotizacion WHERE id_user IN (SELECT id FROM subordinates)
            ORDER BY timestamp DESC
        """)
        result = session.execute(query, {"user_id": id_user})
        cotizaciones = [Cotizacion(**dict(row._mapping)) for row in result.fetchall()]

    else:
        # Operador solo ve las suyas
        cotizaciones = session.exec(
            select(Cotizacion).where(Cotizacion.id_user == id_user).order_by(desc(Cotizacion.timestamp))
        ).all()
    
    return cotizaciones

@router.get("/cotizacion/buscar/", response_model=List[Cotizacion])
async def buscador_cotizaciones(
    session: SessionDep,
    estatus: Optional[int] = Query(None),
    fin: Optional[int] = Query(None),
    broker: Optional[int] = Query(None),
    folioUserRfc: Optional[str] = Query(None),
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    user: Optional[int] = Query(None),
    rol: Optional[str] = Query(None),
    ):
    rows = [] 
    
    if estatus is None and fin is None and not folioUserRfc and not fechaDesde and not fechaHasta and not broker:
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
    # LAB
    # ids = [obj.id_cotizacion for obj in rows]
    # print(ids)
    # idsList = []
    # for num in ids:
    #     numBytes = str(num).encode('utf-8')
    #     base64_bytes = base64.b64encode(numBytes)
    #     cotizacionB64 = base64_bytes.decode('utf-8')
    #     idsList.append(cotizacionB64)
    # print(idsList)
    # LAB
    return rows

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