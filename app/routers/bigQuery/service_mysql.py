    
def get_brokers_mysql(session):
    result = session.execute("""
        SELECT id, nombre, activo
        FROM brokers
    """)
    return [dict(row) for row in result]