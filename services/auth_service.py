import mysql.connector


# 🔐 intentar login
def login(username, password):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=username,
            password=password
        )

        conn.close()
        return True

    except:
        return False


# 🧠 obtener privilegios
def obtener_privilegios(admin_user, admin_pass, username):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=admin_user,
            password=admin_pass
        )

        cursor = conn.cursor()

        cursor.execute(f"SHOW GRANTS FOR '{username}'@'localhost'")
        grants = cursor.fetchall()

        conn.close()

        permisos = " ".join([g[0] for g in grants])

        return permisos

    except Exception as e:
        print("ERROR PRIVILEGIOS:", e)
        return ""