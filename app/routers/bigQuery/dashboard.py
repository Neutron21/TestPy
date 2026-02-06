from fastapi import APIRouter, Depends, HTTPException
from app.services.mysql_service import get_brokers_mysql
from app.services.bigquery_service import (
    truncate_table,
    insert_rows
)

router = APIRouter(prefix="/sync/bigquery", tags=["BigQuery Sync"])
@router.get("/dashboard")
async def update_dashboard(session: SessionDep):
    client = bigquery.Client()
    query = """
    SELECT CURRENT_TIMESTAMP() AS now
    """
    result = client.query(query)

    for row in result:
        print("Conectado a BigQuery:", row.now)