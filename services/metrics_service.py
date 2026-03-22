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

def obtener_threads_running():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SHOW STATUS LIKE 'Threads_running'")
    val = cursor.fetchone()[1]
    conn.close()
    return int(val)


def obtener_bytes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SHOW STATUS LIKE 'Bytes_received'")
    recibidos = int(cursor.fetchone()[1])

    cursor.execute("SHOW STATUS LIKE 'Bytes_sent'")
    enviados = int(cursor.fetchone()[1])

    conn.close()
    return recibidos, enviados


def obtener_slow_queries():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SHOW STATUS LIKE 'Slow_queries'")
    val = cursor.fetchone()[1]

    conn.close()
    return int(val)