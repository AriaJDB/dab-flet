# services/query_service.py
from db_config import conectar

def ejecutar_query(database: str, query: str):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(f"USE `{database}`")
        cursor.execute(query)

        # Si la consulta devuelve resultados (SELECT)
        if cursor.description:
            columnas = [col[0] for col in cursor.description]
            filas = cursor.fetchall()
            conn.close()
            return {
                "tipo": "select",
                "columnas": columnas,
                "filas": filas
            }
        else:
            # Para INSERT, UPDATE, DELETE, etc.
            conn.commit()
            filas_afectadas = cursor.rowcount
            conn.close()
            return {
                "tipo": "accion",
                "filas_afectadas": filas_afectadas
            }

    except Exception as e:
        conn.close()
        raise Exception(str(e))