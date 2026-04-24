from google.cloud import bigquery
from google.api_core.exceptions import NotFound


client = bigquery.Client()

def ensure_table(dataset, table, schema):
    table_id = f"{client.project}.{dataset}.{table}"

    try:
        client.get_table(table_id)
        print(f"✅ Tabla {table} ya existe")
    except NotFound:
        print(f"⚠️ Tabla {table} no existe, creando...")
        new_table = bigquery.Table(table_id, schema=schema)
        client.create_table(new_table)
        print(f"🚀 Tabla {table} creada")

def truncate_table(dataset, table):
    query = f"TRUNCATE TABLE `{dataset}.{table}`"
    client.query(query).result()

def insert_rows(dataset, table, rows):
    table_ref = f"{dataset}.{table}"
    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        raise RuntimeError(errors)
    
SCHEMAS = {
    "brokers": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
    "categorias": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
    "cotizacion": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
        bigquery.SchemaField("email", "STRING"),
    ],
    "estatus_tramites": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
    "financieras": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
    "productos": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
    "sedes": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
    "subCategorias": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
     "usuarios": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
        bigquery.SchemaField("email", "STRING"),
    ],
}