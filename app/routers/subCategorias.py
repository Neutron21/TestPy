from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import text
from app.db import SessionDep
from app.models import SubCategorias

router = APIRouter(tags=["SubCategorias"])

class ProductoPorMembresiaResponse(BaseModel):
    # nombre: str
    sector: str
    subcategoria: str
    instituciones: set[str]


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


@router.get(
    "/subCategorias/catalogo/{id_membresia}",
    response_model=list[ProductoPorMembresiaResponse],
)
async def get_catalogo_by_membership(
    id_membresia: int, session: SessionDep
):
    query = text("""
        SELECT DISTINCT
            p.nombre AS nombre,
            c.nombre AS sector,
            COALESCE(sc.nombre, '') AS subcategoria,
            f.nombre AS institucion
        FROM productos p
        JOIN categorias c
            ON c.id = p.id_categoria
        LEFT JOIN subCategorias sc
            ON sc.id = p.id_subCategoria
        JOIN financieras f
            ON f.id = p.institucion_id
        WHERE f.fase != 0
            AND f.id_membresia <= :id_membresia
        ORDER BY c.nombre, sc.nombre, p.nombre, f.nombre
    """)
    result = session.execute(query, {"id_membresia": id_membresia})

    catalogo: dict[tuple[str, str], ProductoPorMembresiaResponse] = {}
    for row in result.mappings():
        key = (row["sector"], row["subcategoria"])
        if key not in catalogo:
            catalogo[key] = ProductoPorMembresiaResponse(
                # nombre=row["nombre"],
                sector=row["sector"],
                subcategoria=row["subcategoria"],
                instituciones=set(),
            )
        catalogo[key].instituciones.add(row["institucion"])

    return list(catalogo.values())
