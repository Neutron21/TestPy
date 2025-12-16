import base64
import os
from pathlib import Path
import re
import tempfile
from typing import List
import zipfile
from fastapi import APIRouter, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from app.utils.logger_config import logger

router = APIRouter(tags=["Files"])
main_path = os.getenv("RUTA_COTIZACIONES")  


@router.get("/getFiles/{idCotizacion}", response_model=List[str])
async def get_lista_docs(idCotizacion: int):
    try:
        id_b64 = base64.b64encode(str(idCotizacion).encode("utf-8")).decode("utf-8")

        carpeta_adjuntos = os.path.join(main_path, id_b64)
        print(carpeta_adjuntos)
        if not os.path.isdir(carpeta_adjuntos):
            return []  # Carpeta no existe, devolver array vacío

        archivos = os.listdir(carpeta_adjuntos)

        extensiones_validas = re.compile(r'\.(pdf|rar|zip|jpg|png|doc|docx|xls|xlsx|ppt|pptx)$', re.IGNORECASE)

        adjuntos_validos = [
            archivo for archivo in archivos
            if os.path.isfile(os.path.join(carpeta_adjuntos, archivo)) and extensiones_validas.search(archivo)
        ]

        return adjuntos_validos

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ocurrió un error: {str(e)}")
    
@router.post("/uploadFiles")
async def carga_archivos_endpoint(request: Request):
    # 👀 Este no se puede probar en SWAGGER 👀
    try:
        form = await request.form()

        user = form.get("user")
        id_cotizacion = form.get("idCotizacion")
        if not user or not id_cotizacion:
            raise HTTPException(status_code=400, detail="Faltan campos obligatorios.")

        carpeta = f"{main_path}/{id_cotizacion}/"
        print(carpeta)
        os.makedirs(carpeta, exist_ok=True)

        archivos_subidos = []
        print(form.multi_items())
        for key, valor in form.multi_items():
            if key.startswith("file"):
                index = key.replace("file", "")
                archivo: UploadFile = valor
                custom_name_key = f"customName{index}"
                custom_name = form.get(custom_name_key, archivo.filename)

                ruta_destino = os.path.join(carpeta, custom_name)
                print(f"rt: {ruta_destino}")
                with open(ruta_destino, "wb") as f:
                    contenido = await archivo.read()
                    f.write(contenido)

                archivos_subidos.append(custom_name)

        return JSONResponse(content={"message": "Archivos subidos correctamente", "archivos": archivos_subidos})
    except Exception as e:
        logger.error(f"Request: {request}")
        logger.error(f"❌ Error al cargar documentos: {str(e)}")
        return JSONResponse(content={"mensaje": {str(e)}})

@router.get("/download-zip")
def descargar_zip(numCotizacion: str = Query(..., description="Número de cotización en b64")):
    try:

        cotizacion_decode = base64.b64decode(numCotizacion.encode()).decode()
        carpeta = os.path.join(main_path, numCotizacion)

        if not os.path.isdir(carpeta):
            raise HTTPException(status_code=404, detail="No se encontró la carpeta de la cotización.")

        # Obtener archivos válidos
        archivos_validos = []
        for archivo in os.listdir(carpeta):
            ruta = os.path.join(carpeta, archivo)
            if os.path.isfile(ruta) and archivo.lower().endswith(('.pdf', '.rar', '.zip', '.jpg', '.png', 'docx','xlsx')):
                archivos_validos.append(ruta)

        if not archivos_validos:
            raise HTTPException(status_code=404, detail="No hay archivos válidos para descargar.")

        # Crear archivo ZIP temporal
        temp_dir = tempfile.gettempdir()
        nombre_zip = f"cotizacion_{cotizacion_decode}.zip"
        ruta_zip = os.path.join(temp_dir, nombre_zip)

        with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for ruta_archivo in archivos_validos:
                zipf.write(ruta_archivo, arcname=os.path.basename(ruta_archivo))

        # Preparar la respuesta con StreamingResponse
        def iterfile():
            with open(ruta_zip, mode="rb") as f:
                yield from f
            os.remove(ruta_zip)  # Eliminar archivo después de servir

        return StreamingResponse(iterfile(), media_type="application/zip", headers={
            "Content-Disposition": f'attachment; filename="{nombre_zip}"'
        })

    except Exception as e:
        logger.error(f"numCotizacion: {numCotizacion}")
        logger.error(f"❌ Error al descargar zip: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/download-file")
def descarga_formato(
    fileName: str = Query(..., alias="fileName"),
    type: str = Query(...),
    idFinanciera: str = Query(...)
):
    base_dir = Path(os.getenv("RUTA_STORE"))# Ruta absoluta a tu carpeta store
    
    
    ruta_archivo = base_dir / type / idFinanciera / Path(fileName).name

    if ruta_archivo.exists() and ruta_archivo.is_file():
        return FileResponse(
            path=ruta_archivo,
            filename=ruta_archivo.name,
            media_type='application/octet-stream'
        )
    else:
        raise HTTPException(status_code=404, detail="El archivo no existe.")