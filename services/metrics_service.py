from db_config import conectar


def obtener_conexiones():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
    valor = cursor.fetchone()[1]

    conn.close()
    return int(valor)


def obtener_queries():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SHOW STATUS LIKE 'Questions'")
    valor = cursor.fetchone()[1]

    conn.close()
    return int(valor)