from fastapi import APIRouter
from sqlmodel import select, text
from app.db import SessionDep
from app.models import Brokers
from fastapi import HTTPException



router = APIRouter(tags=["Brokers"])

@router.get("/brokers", response_model=list[Brokers])
async def list_brokers(session: SessionDep):
    query = select(Brokers).order_by(Brokers.nombre)
    brokers = session.exec(query).all()
    return brokers

@router.get("/brokers/subordinados", response_model=list[Brokers])
async def list_brokers(id_user: int, session: SessionDep):
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
    result = session.execute(query, {"user_id": id_user})

    return result

@router.post("/brokers", response_model=Brokers)
async def create_broker(broker: Brokers, session: SessionDep):
    # Verificar si ya existe un broker con ese nombre
    existing = session.exec(select(Brokers).where(Brokers.nombre == broker.nombre)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Broker ya existe")

    session.add(broker)
    session.commit()
    session.refresh(broker)
    return broker