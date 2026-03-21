from db_config import conectar

def insertar_registro(database, tabla, valores):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(f"USE {database}")

        columnas = ", ".join(valores.keys())
        placeholders = ", ".join(["%s"] * len(valores))
        datos = list(valores.values())

        query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"

        cursor.execute(query, datos)
        conn.commit()

    except Exception as e:
        print("ERROR INSERT:", e)
        raise e

    finally:
        conn.close()

def obtener_tablas(database):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"USE {database}")
    cursor.execute("SHOW TABLES")

    tablas = [t[0] for t in cursor.fetchall()]
    conn.close()

    return tablas


# 📊 Obtener columnas
def obtener_columnas(database, tabla):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"USE {database}")
    cursor.execute(f"DESCRIBE {tabla}")

    columnas = cursor.fetchall()
    conn.close()

    return columnas


def obtener_registros(database, tabla):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"USE {database}")
    cursor.execute(f"SELECT * FROM {tabla}")

    registros = cursor.fetchall()
    nombres_columnas = [desc[0] for desc in cursor.description]

    conn.close()

    return nombres_columnas, registros

def crear_tabla(database, nombre_tabla, columnas):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(f"USE {database}")

        columnas_sql = ["id INT AUTO_INCREMENT PRIMARY KEY"]

        for col in columnas:
            columnas_sql.append(f"{col['nombre']} {col['tipo']}")

        query = f"CREATE TABLE {nombre_tabla} ({', '.join(columnas_sql)})"

        cursor.execute(query)

        conn.commit()  # 🔥 ESTA ES LA CLAVE

    except Exception as e:
        print("ERROR SQL:", e)
        raise e

    finally:
        conn.close()


# 🗑️ Eliminar tabla
def eliminar_tabla(database, nombre_tabla):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"USE {database}")
    cursor.execute(f"DROP TABLE {nombre_tabla}")

    conn.commit()

    conn.close()