import csv
from db_config import conectar

def exportar_csv(database, tabla, ruta):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE `{database}`")
        cursor.execute(f"SELECT * FROM `{tabla}`")

        filas = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columnas) # Escribir encabezados
            writer.writerows(filas) # Escribir datos
        return True
    except Exception as e:
        print(f"Error Export: {e}")
        return False
    finally:
        conn.close()

def importar_csv(database, tabla, ruta):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE `{database}`")
        with open(ruta, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            columnas = next(reader)

            placeholders = ", ".join(["%s"] * len(columnas))
            columnas_sql = ", ".join([f"`{c}`" for c in columnas])

            query = f"INSERT INTO `{tabla}` ({columnas_sql}) VALUES ({placeholders})"

            for fila in reader:
                if any(fila):
                    cursor.execute(query, fila)

        conn.commit()
        return True
    except Exception as e:
        print(f"Error Import: {e}")
        return False
    finally:
        conn.close()