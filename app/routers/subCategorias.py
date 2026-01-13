from fastapi import APIRouter, HTTPException, status
from sqlmodel import text
from app.db import SessionDep
from app.models import SubCategorias

router = APIRouter(tags=["SubCategorias"])

@router.get("/subCategorias/{id_membresia}", response_model=list[SubCategorias])
async def get_subCategorias_by_Membership(id_membresia: int, session: SessionDep):
    
    query = text("""
            SELECT DISTINCT sc.*
                FROM subCategorias sc
                JOIN productos p 
                    ON p.id_subcategoria = sc.id
                JOIN financieras f 
                    ON f.id = p.institucion_id
                WHERE 
                    f.fase != 0
                    AND f.id_membresia <= :id_membresia;
        """)
    result = session.execute(query, {"id_membresia": id_membresia})
    return result.mappings().all()

