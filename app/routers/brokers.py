from fastapi import APIRouter, HTTPException
from sqlmodel import select, text
from app.db import SessionDep
from app.models import Brokers


router = APIRouter(tags=["Brokers"])

# ---------------------------------------------------
# LISTA DE BROKERS
# ---------------------------------------------------
@router.get("/brokers", response_model=list[Brokers])
async def list_brokers(session: SessionDep):
    query = select(Brokers).order_by(Brokers.nombre)
    brokers = session.exec(query).all()
    return brokers


# ---------------------------------------------------
# LISTA DE BROKERS SUBORDINADOS
# ---------------------------------------------------
@router.get("/brokers/subordinados", response_model=list[Brokers])
async def list_brokers_subordinados(id_user: int, session: SessionDep):

    query = text("""
        WITH RECURSIVE subordinates AS (
            SELECT id, id_broker FROM usuarios WHERE id = :user_id
            UNION ALL
            SELECT u.id, u.id_broker
            FROM usuarios u
            INNER JOIN subordinates s ON u.id_superior = s.id
        )
        SELECT DISTINCT b.*
        FROM brokers b
        JOIN subordinates s ON b.id = s.id_broker
        WHERE s.id != :user_id;
    """)

    result = session.execute(query, {"user_id": id_user}).all()

    # Convertir filas a objetos Brokers
    brokers = [Brokers(id=row.id, nombre=row.nombre) for row in result]

    return brokers


# ---------------------------------------------------
# CREAR BROKER
# ---------------------------------------------------
@router.post("/brokers", response_model=Brokers)
async def create_broker(broker: Brokers, session: SessionDep):

    # Verificar si ya existe
    existing = session.exec(
        select(Brokers).where(Brokers.nombre == broker.nombre)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Broker ya existe")

    session.add(broker)
    session.commit()
    session.refresh(broker)
    return broker
