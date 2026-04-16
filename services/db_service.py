from db_config import conectar

def obtener_bases(session_data=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    todas_las_bases = [db[0] for db in cursor.fetchall()]
    conn.close()

    if not session_data:
        return todas_las_bases

    permisos = session_data.get("permisos", {})
    
    if permisos.get("es_admin"):
        return todas_las_bases

    bd_autorizadas = permisos.get("permisos_bd", {}).keys()
    
    bd_autorizadas_clean = [b.lower().strip() for b in bd_autorizadas]

    return [
        db for db in todas_las_bases 
        if db.lower().strip() in bd_autorizadas_clean
    ]


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