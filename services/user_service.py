from db_config import conectar

def obtener_usuarios():
    """Obtiene la lista de todos los usuarios registrados en el servidor."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT User, Host FROM mysql.user")
        usuarios = cursor.fetchall()
        return usuarios
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def crear_usuario(username, password):
    """Crea un nuevo usuario en el servidor local."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        query = f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}'"
        cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def otorgar_permisos(username, database, permisos):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # --- LÓGICA DE NIVEL DE PRIVILEGIO ---
        # Privilegios que SOLO pueden ser globales (*.*)
        privilegios_globales = ["ALL PRIVILEGES", "SHOW DATABASES", "CREATE USER", "GRANT OPTION"]
        
        # Si el permiso está en la lista global o el usuario eligió "*", usamos *.*
        if permisos.upper() in privilegios_globales or database == "*":
            target = "*.*"
        else:
            target = f"`{database}`.*"

        # 1. Intentar limpiar permisos previos en ese nivel (opcional, evita errores 1221)
        try:
            cursor.execute(f"REVOKE ALL PRIVILEGES ON {target} FROM '{username}'@'localhost'")
        except:
            pass 

        # 2. Asignar el nuevo permiso con el target correcto
        query = f"GRANT {permisos} ON {target} TO '{username}'@'localhost'"
        cursor.execute(query)
        
        conn.commit()
        return True
    except Exception as e:
        # Imprimimos el error exacto en consola para depurar
        print(f"ERROR AL EDITAR PERMISOS ({permisos} en {target}): {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def eliminar_usuario(username):
    """Elimina permanentemente a un usuario del servidor."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        query = f"DROP USER '{username}'@'localhost'"
        cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def aplicar_cambios():
    """Refresca la tabla de privilegios de MariaDB/MySQL."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("FLUSH PRIVILEGES")
        return True
    except Exception as e:
        print(f"Error al aplicar cambios: {e}")
        return False
    finally:
        cursor.close()
        conn.close()