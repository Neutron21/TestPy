import time
from fastapi import FastAPI, Request
from datetime import datetime

from app.models import Invoice
from app.db import create_all_tables
from .routers import customers, transactions, plans, financieras, productos, usuarios, formatos, producto_formato, cotizacion

app = FastAPI()

app.include_router(financieras.router)
app.include_router(productos.router)
app.include_router(usuarios.router)
app.include_router(formatos.router)
app.include_router(producto_formato.router)
app.include_router(cotizacion.router)




@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
   
    print(f"Request: {request.url} completed in: {process_time:.4f} seconds")

    return response