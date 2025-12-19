import os
import shutil
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.utils.logger_config import logger

# 🔹 Carga las variables del entorno de producción
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv("/root/TestPy/.env")

# 🔹 Configuración de la conexión a la BD
DB_HOST = os.getenv("SQL_HOST")
DB_USER = os.getenv("SQL_USER")
DB_PASSWORD = os.getenv("SQL_PASS", "").replace("'", "")  
DB_NAME = os.getenv("SQL_DB_NAME")
DB_PORT = os.getenv("SQL_PORT", 3306)

if not DB_HOST:
    raise RuntimeError("DB_HOST no está definido")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# 🔎 Obtiene IDs de cotizaciones que contienen "prueba"
def obtener_ids_prueba():
    session = Session()
    try:
        db = session.execute(text("SELECT DATABASE()")).scalar()
        print("🧠 Conectado a la BD:", db)

        result = session.execute(text("""
            SELECT id_cotizacion
            FROM cotizacion
            WHERE LOWER(nombre) LIKE '%prueba%'
        """))

        ids = [str(row.id_cotizacion) for row in result]
        print("🔎 IDs encontrados:", ids)
        return ids
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error obtener_ids_prueba: {str(e)}")
    finally:
        session.close()

# 🗑 Borra carpetas por ID
def borrar_carpetas(ids):
    base_path = os.getenv("RUTA_COTIZACIONES")

    if not base_path:
        print("❌ RUTA_COTIZACIONES no definida")
        return

    for cot_id in ids:
        ruta = os.path.join(base_path, cot_id)

        if os.path.exists(ruta):
            shutil.rmtree(ruta)
            print(f"🗑 Carpeta eliminada: {ruta}")
        else:
            print(f"⚠️ Carpeta no encontrada: {ruta}")
            

# 🧨 Borra registros en BD
def borrar_cotizaciones_prueba():
    session = Session()
    try:
        db = session.execute(text("SELECT DATABASE()")).scalar()
        print("🧠 Borrando en BD:", db)

        result = session.execute(text("""
            DELETE FROM cotizacion
            WHERE LOWER(nombre) LIKE '%prueba%'
        """))

        print(f"🧨 Filas eliminadas: {result.rowcount}")
        session.commit()
        print("✅ Cotizaciones eliminadas de MySQL")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error MySQL: {str(e)}")


    finally:
        session.close()

def job_borrado_prod():
    ids = obtener_ids_prueba()
    if not ids:
        print("ℹ️ No hay cotizaciones con 'prueba'")
        return

    borrar_carpetas(ids)
    borrar_cotizaciones_prueba()

if __name__ == "__main__":
    job_borrado_prod()
