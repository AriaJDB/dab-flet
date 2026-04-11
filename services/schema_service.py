from db_config import conectar

def obtener_esquema(database: str):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"USE `{database}`")
    cursor.execute("SHOW TABLES")
    tablas = [t[0] for t in cursor.fetchall()]

    esquema = {}
    for tabla in tablas:
        cursor.execute(f"SHOW COLUMNS FROM `{tabla}`")
        columnas = [c[0] for c in cursor.fetchall()]
        esquema[tabla] = columnas

    conn.close()
    return esquema