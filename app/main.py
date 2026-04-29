from datetime import datetime
from jwt import decode as jwt_decode
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
from app.routers import procesos 
from app.utils.logger_config import logger

from fastapi.staticfiles import StaticFiles

from .routers import ( checklist, membresias, tareas, utms, documentos,viabilidad, 
    financieras, productos, usuarios, formatos, producto_formato, cotizacion, comentarios, correos, estatus_tramites, 
    send_mail, uploadFiles, utils, brokers, procesos, sedes)
from .routers.pagos import (pagos)
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate("app/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
PUBLIC_ROUTES = os.getenv("PUBLIC_ROUTES", "").split(",")
ALLOW_SERVERS = os.getenv("ALLOW_SERVERS", "").split(",")

app = FastAPI(
    title="API de Konnect",
    description="API protegida con JWT de Firebase",
    version="1.0"
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "utils", "static"), html=False),
    name="static"
)

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
app.include_router(brokers.router)
app.include_router(checklist.router)
app.include_router(comentarios.router)
app.include_router(correos.router)
app.include_router(cotizacion.router)
app.include_router(documentos.router)
app.include_router(estatus_tramites.router)
app.include_router(financieras.router)
app.include_router(formatos.router)
app.include_router(producto_formato.router)
app.include_router(membresias.router)
app.include_router(pagos.router)
app.include_router(productos.router)
app.include_router(procesos.router)
app.include_router(send_mail.router)
app.include_router(uploadFiles.router)
app.include_router(usuarios.router)
app.include_router(utils.router)
app.include_router(utms.router)
app.include_router(viabilidad.router)
app.include_router(sedes.router)
app.include_router(tareas.router)
app.include_router(brokers.router)


logger.info("API iniciada correctamente 🚀")
# # 🔹 Middleware de autenticación Firebase
class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        if any(request.url.path.startswith(route) for route in PUBLIC_ROUTES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return self.unauthorized("Token requerido")

        token = auth_header.split(" ")[1]

        try:
            decoded_token = auth.verify_id_token(token, clock_skew_seconds=60)

            firebase_project_id = os.getenv("ID_PROJECT")
            if decoded_token["aud"] != firebase_project_id:
                raise ValueError("Token inválido para este proyecto")

            request.state.user = decoded_token

        except Exception as e:
            # return self.unauthorized(f"Token inválido: {str(e)}")
            try:
                decoded_unverified = jwt_decode(token, options={"verify_signature": False})

                now = datetime.datetime.utcnow().timestamp()
                iat = decoded_unverified.get("iat")
                exp = decoded_unverified.get("exp")

                if iat and iat > now + 5:
                    logger.error(f"⏱️ Token del FUTURO detectado. iat: {iat}, now: {now}")
                    return self.unauthorized("El reloj del dispositivo está adelantado")

                if exp and exp < now:
                    logger.error(f"⌛ Token EXPIRADO. exp: {exp}, now: {now}")
                    return self.unauthorized("Sesión expirada, inicia sesión nuevamente")

                logger.error(f"❌ Error desconocido en token: {str(e)}")
                return self.unauthorized("Token inválido")

            except Exception as decode_error:
                logger.error(f"🔥 No se pudo decodificar el token: {str(decode_error)}")
                return self.unauthorized("Token inválido. No se pudo decodificar")

        return await call_next(request)

    def unauthorized(self, message: str):
        return JSONResponse(
            status_code=401,
            content={"detail": message},
            headers={
                "Access-Control-Allow-Origin": "*",  # o usa el origen permitido si lo quieres restringido
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*",
            }
        )

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
    allow_origins=ALLOW_SERVERS,            # Permitir solo estos orígenes
    allow_credentials=True,
    allow_methods=["*"],              # Permitir todos los métodos: GET, POST, etc.
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"] # Permitir todos los headers
)
app.add_middleware(FirebaseAuthMiddleware)