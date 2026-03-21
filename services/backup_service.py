import subprocess
import os

def hacer_backup(database, user, password, ruta_archivo):
    try:
        comando = [
            "mysqldump",
            "-u", user,
            f"-p{password}",
            database
        ]

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            subprocess.run(comando, stdout=f, check=True)

        return True

    except Exception as e:
        print("ERROR BACKUP:", e)
        return False


def restaurar_backup(database, user, password, ruta_archivo):
    try:
        comando = [
            "mysql",
            "-u", user,
            f"-p{password}",
            database
        ]

        with open(ruta_archivo, "r", encoding="utf-8") as f:
            subprocess.run(comando, stdin=f, check=True)

        return True

    except Exception as e:
        print("ERROR RESTORE:", e)
        return False