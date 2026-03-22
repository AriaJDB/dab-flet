import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

RUTA_DUMP = os.getenv("DB_DUMP_PATH", "mariadb-dump")
RUTA_MYSQL = os.getenv("DB_CLI_PATH", "mariadb")

def hacer_backup(database, user, password, ruta_archivo):
    if not os.path.exists(RUTA_DUMP):
        print(f"Error: No se encontró el ejecutable en {RUTA_DUMP}")
        return False

    try:
        comando = [
            RUTA_DUMP,
            f"--user={user}",
            f"--password={password}",
            "--databases",
            database
        ]

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            proceso = subprocess.run(
                comando, 
                stdout=f, 
                stderr=subprocess.PIPE, 
                text=True,
                shell=False # Con ruta absoluta, es mejor shell=False
            )

        if proceso.returncode != 0:
            print(f"ERROR DE MYSQLDUMP: {proceso.stderr}")
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            return False

        return True

    except Exception as e:
        print("ERROR CRÍTICO EN SERVICE:", e)
        return False

def restaurar_backup(database, user, password, ruta_archivo):
    if not os.path.exists(ruta_archivo):
        return False

    try:
        comando = [
            RUTA_MYSQL,
            f"--user={user}",
            f"--password={password}",
            database
        ]

        with open(ruta_archivo, "r", encoding="utf-8") as f:
            proceso = subprocess.run(
                comando, 
                stdin=f, 
                stderr=subprocess.PIPE, 
                text=True,
                shell=False
            )

        if proceso.returncode != 0:
            print(f"ERROR DE RESTORE: {proceso.stderr}")
            return False

        return True

    except Exception as e:
        print("ERROR RESTORE SERVICE:", e)
        return False