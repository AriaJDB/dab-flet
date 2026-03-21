from db_config import conectar

def obtener_bases():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SHOW DATABASES")
    bases = [db[0] for db in cursor.fetchall()]

    conn.close()
    return bases


def crear_base(nombre):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE {nombre}")

    conn.close()


def eliminar_base(nombre):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"DROP DATABASE {nombre}")

    conn.close()