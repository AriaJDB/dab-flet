from db_config import conectar


# 👤 Crear usuario MariaDB
def crear_usuario(username, password):
    conn = conectar()
    cursor = conn.cursor()

    try:
        query = f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}'"
        cursor.execute(query)
        conn.commit()
        return True

    except Exception as e:
        print("ERROR CREATE USER:", e)
        return False

    finally:
        conn.close()


# 🔐 Asignar permisos (rol básico)
def otorgar_permisos(username, database, permisos):
    conn = conectar()
    cursor = conn.cursor()

    try:
        query = f"GRANT {permisos} ON {database}.* TO '{username}'@'localhost'"
        cursor.execute(query)
        conn.commit()
        return True

    except Exception as e:
        print("ERROR GRANT:", e)
        return False

    finally:
        conn.close()


# 🔄 Aplicar cambios
def aplicar_cambios():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("FLUSH PRIVILEGES")
    conn.close()


# 📋 Ver usuarios
def obtener_usuarios():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT User, Host FROM mysql.user")
    usuarios = cursor.fetchall()

    conn.close()
    return usuarios