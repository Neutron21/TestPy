import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import firebase_admin
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from firebase_admin import auth, credentials
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_all_tables
<<<<<<< HEAD
from .routers import financieras, productos, usuarios, formatos, producto_formato, cotizacion, comentarios, correos, estatus_tramites, send_mail, uploadFiles,utils
=======
from .routers import ( checklist,
    financieras, productos, usuarios, formatos, producto_formato, cotizacion, comentarios, correos, estatus_tramites, send_mail, uploadFiles)
>>>>>>> 2f0e404765f2b980cd03efa440a100ebefbf04f9
from dotenv import load_dotenv


load_dotenv()

cred = credentials.Certificate("app/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
PUBLIC_ROUTES = os.getenv("PUBLIC_ROUTES", "").split(",")

app = FastAPI(
    title="API de Konnect",
    description="API protegida con JWT de Firebase",
    version="1.0"
)
origins = [
    "http://localhost:4200",  # Angular en local
    "http://127.0.0.1:4200",
    # Agrega aquí otros dominios si lo despliegas
]
original_openapi = app.openapi
# 🔹 Función personalizada para OpenAPI con seguridad JWT
def custom_openapi():
    if not app.openapi_schema:
        openapi_schema = original_openapi()  # ⬅ Aquí usamos el original, no recursivo
        openapi_schema["components"] = openapi_schema.get("components", {})
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        for path in openapi_schema["paths"]:
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = [{"bearerAuth": []}]
        app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi  # 🔹 Sobrescribe la función de OpenAPI

# 🔹 Incluir routers
app.include_router(financieras.router)
app.include_router(productos.router)
app.include_router(usuarios.router)
app.include_router(formatos.router)
app.include_router(producto_formato.router)
app.include_router(cotizacion.router)
app.include_router(comentarios.router)
app.include_router(correos.router)
app.include_router(estatus_tramites.router)
app.include_router(send_mail.router)
app.include_router(uploadFiles.router)
<<<<<<< HEAD
app.include_router(utils.router)
=======
app.include_router(checklist.router)
>>>>>>> 2f0e404765f2b980cd03efa440a100ebefbf04f9


# 🔹 Middleware de autenticación Firebase
class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(route) for route in PUBLIC_ROUTES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Token requerido"})

        token = auth_header.split(" ")[1]

        try:
            decoded_token = auth.verify_id_token(token)  # 🔹 Verificar token con Firebase
            firebase_project_id = os.getenv("ID_PROJECT")  # Cambia esto por el ID real de tu Firebase

            # 🔹 Validar que el token pertenece a este proyecto
            if decoded_token["aud"] != firebase_project_id:
                raise ValueError("Token inválido para este proyecto")

            request.state.user = decoded_token  # Guardar info del usuario autenticado

        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": f"Token inválido: {str(e)}"})

        return await call_next(request)

app.add_middleware(FirebaseAuthMiddleware)

# 🔹 Middleware para medir tiempos de respuesta
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request: {request.url} completed in: {process_time:.4f} seconds")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Permitir solo estos orígenes
    allow_credentials=True,
    allow_methods=["*"],              # Permitir todos los métodos: GET, POST, etc.
    allow_headers=["*"],              # Permitir todos los headers
)
