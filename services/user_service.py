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
        query = f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}'"
        cursor.execute(query)
        conn.commit()
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
        query = f"DROP USER '{username}'@'localhost'"
        cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        return False
    finally:
        conn.close()

# --- NUEVA FUNCIÓN: OBTENER PERMISOS ACTUALES ---
def obtener_permisos_usuario(username):
    """Devuelve una lista de strings con los privilegios que tiene el usuario."""
    conn = conectar()
    cursor = conn.cursor()
    permisos_encontrados = []
    try:
        cursor.execute(f"SHOW GRANTS FOR '{username}'@'localhost'")
        grants = cursor.fetchall()
        
        # Procesamos las líneas de GRANT (suelen venir como 'GRANT SELECT, INSERT ON ...')
        for row in grants:
            linea = row[0].upper()
            # Si tiene ALL PRIVILEGES, lo añadimos y terminamos
            if "ALL PRIVILEGES" in linea:
                return ["ALL PRIVILEGES"]
            
            # Lista de posibles permisos a buscar en la cadena
            posibles = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "EXECUTE", "GRANT OPTION", "SHOW DATABASES"]
            for p in posibles:
                if p in linea:
                    permisos_encontrados.append(p)
                    
        return list(set(permisos_encontrados)) # Quitamos duplicados
    except Exception as e:
        print(f"Error al obtener permisos: {e}")
        return []
    finally:
        conn.close()

def otorgar_permisos(username, database, permisos):
    conn = conectar()
    cursor = conn.cursor()
    try:
        privilegios_globales = ["ALL PRIVILEGES", "SHOW DATABASES", "CREATE USER", "GRANT OPTION"]
        
        if permisos.upper() in privilegios_globales or database == "*":
            target = "*.*"
        else:
            target = f"`{database}`.*"

        # Intentar limpiar antes de asignar el nuevo (opcional)
        try:
            cursor.execute(f"REVOKE ALL PRIVILEGES ON {target} FROM '{username}'@'localhost'")
        except:
            pass 

        query = f"GRANT {permisos} ON {target} TO '{username}'@'localhost'"
        cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f"ERROR GRANT ({permisos}): {e}")
        return False
    finally:
        conn.close()

def aplicar_cambios():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("FLUSH PRIVILEGES")
    finally:
        conn.close()