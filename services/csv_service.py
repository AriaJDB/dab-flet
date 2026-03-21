import csv
from db_config import conectar


# 📤 EXPORTAR CSV
def exportar_csv(database, tabla, ruta):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(f"USE {database}")
        cursor.execute(f"SELECT * FROM {tabla}")

        filas = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columnas)
            writer.writerows(filas)

        return True

    except Exception as e:
        print("ERROR EXPORT:", e)
        return False

    finally:
        conn.close()


# 📥 IMPORTAR CSV
def importar_csv(database, tabla, ruta):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(f"USE {database}")

        with open(ruta, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            columnas = next(reader)

            placeholders = ", ".join(["%s"] * len(columnas))
            columnas_sql = ", ".join(columnas)

            query = f"INSERT INTO {tabla} ({columnas_sql}) VALUES ({placeholders})"

            for fila in reader:
                cursor.execute(query, fila)

        conn.commit()
        return True

    except Exception as e:
        print("ERROR IMPORT:", e)
        return False

    finally:
        conn.close()