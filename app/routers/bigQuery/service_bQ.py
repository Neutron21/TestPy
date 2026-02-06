from google.cloud import bigquery

client = bigquery.Client()

def truncate_table(dataset, table):
    query = f"TRUNCATE TABLE `{dataset}.{table}`"
    client.query(query).result()

def insert_rows(dataset, table, rows):
    table_ref = f"{dataset}.{table}"
    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        raise RuntimeError(errors)