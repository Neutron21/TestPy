import base64
import os
import tempfile
from typing import List, Optional
import zipfile
from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse

router = APIRouter(tags=["Files"])
main_path = os.getenv("RUTA_COTIZACIONES")  

@router.post("/uploadFiles")
async def carga_archivos_endpoint(request: Request):
    # 👀 Este no se puede probar en SWAGGER 👀
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
        raise HTTPException(status_code=400, detail=str(e))
