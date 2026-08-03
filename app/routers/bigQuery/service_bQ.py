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
    print(f"🧹 Truncando tabla {dataset}.{table}")
    query = f"TRUNCATE TABLE `{dataset}.{table}`"
    client.query(query).result()


def insert_rows(dataset, table, rows):
    print(f"🔹 Insertando {len(rows)} filas en {dataset}.{table}...")
    table_ref = f"{dataset}.{table}"
    errors = client.insert_rows_json(table_ref, rows)
    print(f"🔥 Filas insertadas en la tabla {table}")
    if errors:
        print(f"❌ BigQuery insert error en {table}: {errors}")
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
        bigquery.SchemaField("id_cotizacion", "INT64"),
        bigquery.SchemaField("id_usuario", "STRING"), # Mail
        bigquery.SchemaField("id_financiera", "INT64"),
        bigquery.SchemaField("producto", "INT64"),
        bigquery.SchemaField("tipo_persona", "STRING"),
        bigquery.SchemaField("nombre", "STRING"),
        bigquery.SchemaField("rfc", "STRING"),
        bigquery.SchemaField("plazo", "STRING"),
        bigquery.SchemaField("edad", "INT64"),
        bigquery.SchemaField("monto", "INT64"),
        bigquery.SchemaField("ingresos", "INT64"),
        bigquery.SchemaField("estatus", "INT64"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("antiguedad_empresa", "INT64"),
        bigquery.SchemaField("OpCliente", "STRING"),
        bigquery.SchemaField("broker", "INT64"),
        bigquery.SchemaField("sede", "INT64"),
        bigquery.SchemaField("custom_prod", "STRING"),
        bigquery.SchemaField("destinoCredito", "STRING"),
        bigquery.SchemaField("id_user", "INT64"),
        bigquery.SchemaField("fecha_pago", "DATE"),
    ],
    "estatus_tramites": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("name", "STRING"),
    ],
    "financieras": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
        bigquery.SchemaField("tipo", "STRING"),
        bigquery.SchemaField("fase", "INT64"),
        bigquery.SchemaField("id_membresia ", "INT64"),
    ],
    "productos": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
        bigquery.SchemaField("institucion_id", "INT64"),
        bigquery.SchemaField("id_categoria", "INT64"),
        bigquery.SchemaField("id_subCategoria", "INT64"),
        bigquery.SchemaField("plazo", "STRING"),
    ],
    "sedes": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
    "subCategorias": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("id_categoria", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
     "usuarios": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
        bigquery.SchemaField("email", "STRING"),
        bigquery.SchemaField("rol", "STRING"),
        bigquery.SchemaField("rfc", "STRING"),
        bigquery.SchemaField("id_broker", "INT64"),
        bigquery.SchemaField("id_sede", "INT64"),
        bigquery.SchemaField("membresia", "INT64"),
        bigquery.SchemaField("celular", "STRING"),
        bigquery.SchemaField("nivel", "INT64"),
        bigquery.SchemaField("id_superior", "INT64"),
        bigquery.SchemaField("id_financiera", "INT64"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("comisiones", "STRING"),
        bigquery.SchemaField("f_ultimo_pago", "DATE"),
    ],
    "comentarios": [
        bigquery.SchemaField("id_comentario", "INT64"),
        bigquery.SchemaField("id_cotizacion", "INT64"),
        bigquery.SchemaField("id_usuario", "STRING"),
        bigquery.SchemaField("comentarios", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("visible", "BOOL"),
    ],
    "membresias": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("nombre", "STRING"),
    ],
    "track_status": [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("id_cotizacion", "INT64"),
        bigquery.SchemaField("id_status", "INT64"),
        bigquery.SchemaField("fecha", "TIMESTAMP"),
        bigquery.SchemaField("id_usuario", "STRING"),
    ],
}