from db_config import conectar

def obtener_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT User, Host FROM mysql.user")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        conn.close()


def crear_usuario(username, password):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"CREATE USER IF NOT EXISTS '{username}'@'localhost' IDENTIFIED BY '{password}'"
        )
        conn.commit()
        cursor.execute("FLUSH PRIVILEGES")
        return True
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        return False
    finally:
        conn.close()


def eliminar_usuario(username):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DROP USER '{username}'@'localhost'")
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        return False
    finally:
        conn.close()


def obtener_permisos_por_bd(username):
    conn = conectar()
    cursor = conn.cursor()
    permisos_bd = {}

    try:
        cursor.execute(f"SHOW GRANTS FOR '{username}'@'localhost'")
        grants = cursor.fetchall()

        for (grant,) in grants:
            grant = grant.upper()
            if " ON " not in grant:
                continue

            parte_permisos = grant.split("GRANT")[1].split("ON")[0].strip()
            parte_db = grant.split("ON")[1].split("TO")[0].strip()
            
            db_name = parte_db.split(".")[0].replace("`", "").strip().lower()
            
            if db_name == "*": continue 

            lista_p = [p.strip().upper() for p in parte_permisos.split(",")]
            
            if db_name in permisos_bd:
                permisos_bd[db_name].extend(lista_p)
            else:
                permisos_bd[db_name] = lista_p

        return permisos_bd
    except Exception as e:
        print(f"DEBUG Error Service: {e}")
        return {}
    finally:
        conn.close()


def actualizar_permisos_usuario(username, database, permisos):
    conn = conectar()
    cursor = conn.cursor()
    try:
        target = f"`{database}`.*"

        for permiso in ["SELECT", "INSERT", "UPDATE"]:
            try:
                cursor.execute(
                    f"REVOKE {permiso} ON {target} FROM '{username}'@'localhost'"
                )
            except Exception:
                pass

        if permisos:
            permisos_sql = ", ".join(permisos)
            cursor.execute(
                f"GRANT {permisos_sql} ON {target} TO '{username}'@'localhost'"
            )

        conn.commit()
        cursor.execute("FLUSH PRIVILEGES")
        return True

    except Exception as e:
        print(f"Error al actualizar permisos: {e}")
        return False
    finally:
        conn.close()