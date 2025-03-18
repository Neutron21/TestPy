from fastapi import APIRouter, status , HTTPException
from sqlmodel import select
from app.models import Customer, CustomerCreate, CustomerUpdate
from app.db import SessionDep

router = APIRouter(tags=['Customers'])

@router.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

@router.get("/customers", response_model=list[Customer])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()

@router.get("/customers/{customer_id}", response_model=Customer)
async def read_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer no existe")
    return customer_db

@router.patch("/customers/{customer_id}", response_model=Customer,status_code=status.HTTP_201_CREATED)
async def edit_customer(customer_id: int, customer_data: CustomerUpdate, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer no existe")
    customer_data_dict = customer_data.model_dump(exclude_unset=True) 
    customer_db.sqlmodel_update(customer_data_dict)
    
    session.commit()
    session.refresh(customer_db)
    return customer_db

@router.delete("/customers/{customer_id}", response_model=Customer)
async def delete_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer no existe")
    session.delete(customer_db)
    session.commit()

    return {"detail": "Borrado exitoso!"}
