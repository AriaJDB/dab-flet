import mysql.connector

def login(username, password):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=username,
            password=password
        )
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"ERROR LOGIN: {err}")
        return False


def obtener_privilegios(username, password):
    from services.user_service import obtener_permisos_por_bd

    try:
        permisos_bd = obtener_permisos_por_bd(username)

        es_admin = False
        conn = mysql.connector.connect(
            host="localhost",
            user=username,
            password=password
        )
        cursor = conn.cursor()
        cursor.execute(f"SHOW GRANTS FOR '{username}'@'localhost'")
        grants = cursor.fetchall()
        conn.close()

        permisos_bd = obtener_permisos_por_bd(username)
        es_admin = False

        for (grant,) in grants:
            if "ALL PRIVILEGES" in grant.upper() and "*.*" in grant:
                es_admin = True
                break

        return {
            "es_admin": es_admin,
            "permisos_bd": permisos_bd
        }

    except Exception as e:
        print("ERROR PRIVILEGIOS:", e)
        return {"es_admin": False, "permisos_bd": {}}