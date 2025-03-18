import zoneinfo
from fastapi import FastAPI
from datetime import datetime

from app.models import Invoice, Transaction
from app.db import create_all_tables
from .routers import customers

country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}

app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)

@app.get("/")
async def root():
    return {"message": "Hola Mundo!"}

@app.get("/saludo/{name}")
async def saludo(name: str):
    return {"message": f"Hola {name}, es un gusto verte por aca!"}

@app.get("/time/{iso_code}")
async def time(iso_code: str):
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    fecha_hora_actual = datetime.now(tz)
    
    return {
        "time": fecha_hora_actual.strftime("%d-%m-%Y %H:%M:%S"),
        "place": timezone_str
        }


@app.post("/transactions")
async def create_customer(transaction_data: Transaction):
    return transaction_data

@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
