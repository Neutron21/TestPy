import os
from typing import Annotated
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv

load_dotenv()

sql_host = os.getenv("SQL_HOST")
sql_name = os.getenv("SQL_DB_NAME")
sql_user = os.getenv("SQL_USER")
sql_pass = os.getenv("SQL_PASS")
sql_url = f"mysql+pymysql://{sql_user}:{sql_pass}@{sql_host}/{sql_name}"

engine = create_engine(
    sql_url,
    echo=True,
     pool_recycle=3600,
    pool_pre_ping=True)

def create_all_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]