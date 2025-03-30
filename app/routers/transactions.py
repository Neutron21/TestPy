from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select
from app.db import SessionDep
from app.models import PaginatedTransactionsResponse, Transaction, TransactionCreate, Customer

router = APIRouter(tags=["Transactions"])

@router.post("/transactions", status_code=status.HTTP_201_CREATED)
async def create_customer(transaction_data: TransactionCreate, session: SessionDep):
    transaction_data_dict = transaction_data.model_dump()
    customer = session.get(Customer, transaction_data_dict.get('customer_id'))
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer no existe")
    
    transaction_db = Transaction.model_validate(transaction_data_dict)
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)

    return transaction_data

@router.get("/transactions")
async def list_transaction(
    session: SessionDep,
    skip: int = Query(0, description="Resgistros a omitir"), 
    limit: int=Query(10, description="Registros por pagina")
):

    query = select(Transaction).offset(skip).limit(limit)
    transactions = session.exec(query).all()

    # Obtener el total de registros en la base de datos (sin paginación)
    total_count_query = select(Transaction)
    total_count = len(session.exec(total_count_query).all())
    # Calcular el total de páginas
    total_pages = (total_count + limit - 1) // limit  # Redondear hacia arriba

    # Crear la respuesta paginada
    response = PaginatedTransactionsResponse(
        total_count=total_count,
        total_pages=total_pages,
        current_page=(skip // limit) + 1,  # Calcular la página actual
        limit=limit,
        transactions=transactions
    )

    return response