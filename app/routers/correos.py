from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlmodel import select
from app.db import SessionDep
from app.models import Correos, CorreosDTO, Financieras

router = APIRouter(tags=["Correos"])

# 1. RUTAS ESTÁTICAS PRIMERO
@router.get("/correos/activos", response_model=list[Correos])  
async def obtener_todos_los_correos_activos(session: SessionDep):
    query = select(Correos).where(Correos.v_comercial == 1)
    correos = session.exec(query).all()  

    if not correos:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron correos activos")  

    return correos

@router.get("/financieras/con-correos")
async def obtener_financieras_con_correos(session: SessionDep):
    query = text("""
        SELECT 
            f.id AS id_financiera,
            f.nombre AS financiera,
            f.img AS img, 
            c.id_correo AS id_correo,
            c.nombre AS nombre_contacto,
            c.correo AS correo,
            c.telefono AS telefono,
            cat.nombre AS categoria
        FROM financieras f
        LEFT JOIN correos c ON f.id = c.id_financiera
        LEFT JOIN categorias cat ON c.categoria_id = cat.id
        ORDER BY f.nombre ASC, c.correo ASC;
    """)
    
    resultados = session.exec(query).all()

    financieras_dict = {}
    
    for row in resultados:
        nombre_limpio = row.financiera  
        
        if nombre_limpio not in financieras_dict:
            financieras_dict[nombre_limpio] = {
                "id_financiera": row.id_financiera,
                "institucion": nombre_limpio,
                "img": row.img,  
                "contactos": []
            }
        
        if row.correo:
            financieras_dict[nombre_limpio]["contactos"].append({
                "id_correo": row.id_correo,
                "nombre": row.nombre_contacto,
                "correo": row.correo,
                "telefono": row.telefono,
                "puesto": row.categoria if row.categoria else "" 
            })

    financieras_ordenadas = sorted(
        financieras_dict.values(), 
        key=lambda x: x["institucion"].lower()
    )

    return financieras_ordenadas

# 2. RUTAS CON PARÁMETROS DINÁMICOS DESPUÉS
@router.get("/correos/activos/{id_financiera}", response_model=list[Correos])  
async def obtener_correos_activos(id_financiera: int, session: SessionDep):
    query = select(Correos).where(
        (Correos.id_financiera == id_financiera) & (Correos.v_comercial == 1)
    )
    correos = session.exec(query).all()  

    if not correos:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron correos activos para esta financiera")  

    return correos  

@router.get("/correos/{id_financiera}", response_model=list[Correos])  
async def obtener_correos(id_financiera: int, session: SessionDep):
    query = select(Correos).where(Correos.id_financiera == id_financiera)
    correos = session.exec(query).all()  

    if not correos:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron correos para esta financiera")  

    return correos  

# 3. ACCIONES DE ESCRITURA (POST / PUT)
@router.post("/correo", response_model=Correos)
async def create_correo(correo_data: CorreosDTO, session: SessionDep):
    nuevo_correo = Correos.model_validate(correo_data.model_dump())
    session.add(nuevo_correo)
    session.commit()
    session.refresh(nuevo_correo)
    return nuevo_correo

@router.put("/correo/{id_correo}", response_model=Correos)
async def update_correo(id_correo: int, correo_data: CorreosDTO, session: SessionDep):
    correo_existente = session.get(Correos, id_correo)
    if not correo_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correo no encontrado",
        )

    correo_existente.sqlmodel_update(correo_data.model_dump())
    session.commit()
    session.refresh(correo_existente)
    return correo_existente