import zoneinfo
import time
from fastapi import FastAPI, Request
from datetime import datetime

from app.models import Invoice
from app.db import create_all_tables
from .routers import customers, transactions, plans, financieras, productos

country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}

app = FastAPI()
# app.include_router(customers.router)
# app.include_router(transactions.router)
# app.include_router(plans.router)
app.include_router(financieras.router)
app.include_router(productos.router)

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
   
    print(f"Request: {request.url} completed in: {process_time:.4f} seconds")

    return response
    

@app.get("/")
async def root():
    return {"message": "Hola Mundo!"}

@app.get("/saludo/{name}")
async def saludo(name: str):
    return {"message": f"Hola {name}, es un gusto verte por aca!"}

@app.get("/time/{iso_code}")
async def get_time_by_iso_code(iso_code: str):
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    fecha_hora_actual = datetime.now(tz)
    
    return {
        "time": fecha_hora_actual.strftime("%d-%m-%Y %H:%M:%S"),
        "place": timezone_str
        }


@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
