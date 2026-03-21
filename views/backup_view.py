import flet as ft
from services.backup_service import hacer_backup, restaurar_backup
from services.db_service import obtener_bases
import os

# 🧰 tkinter para explorador
import tkinter as tk
from tkinter import filedialog


def backup_view(page: ft.Page):

    dropdown_db = ft.Dropdown(label="Selecciona base de datos", width=300)

    # 📁 Carpeta destino
    ruta_carpeta = ft.TextField(label="Carpeta destino", width=400, read_only=True)

    # 📝 Nombre archivo
    nombre_archivo = ft.TextField(label="Nombre del archivo", width=300)

    # 🔄 cargar bases
    def cargar_bases():
        bases = obtener_bases()
        dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
        page.update()

    # 📂 Explorador de carpetas (tkinter)
    def seleccionar_carpeta(e):
        root = tk.Tk()
        root.withdraw()  # oculta ventana principal

        carpeta = filedialog.askdirectory()

        if carpeta:
            ruta_carpeta.value = carpeta
            page.update()

    # 💾 BACKUP
    def backup(e):
        db = dropdown_db.value
        carpeta = ruta_carpeta.value
        nombre = nombre_archivo.value

        if not db or not carpeta or not nombre:
            page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"))
            page.snack_bar.open = True
            page.update()
            return

        ruta_final = os.path.join(carpeta, f"{nombre}.sql")

        try:
            ok = hacer_backup(db, "root", "latte", ruta_final)

            if ok:
                msg = f"Backup creado con éxito ✅\n{ruta_final}"
            else:
                msg = "Error al crear el backup ❌"

        except Exception as e:
            msg = f"Error: {e}"

        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    # 🔄 RESTAURAR
    def restaurar(e):
        db = dropdown_db.value
        carpeta = ruta_carpeta.value
        nombre = nombre_archivo.value

        if not db or not carpeta or not nombre:
            page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"))
            page.snack_bar.open = True
            page.update()
            return

        ruta_final = os.path.join(carpeta, f"{nombre}.sql")

        try:
            ok = restaurar_backup(db, "root", "latte", ruta_final)

            if ok:
                msg = "Base restaurada con éxito ✅"
            else:
                msg = "Error al restaurar ❌"

        except Exception as e:
            msg = f"Error: {e}"

        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    # 🚀 inicializar
    cargar_bases()

    return ft.Column(
        [
            ft.Text("💾 Backups y Restauración", size=24, weight="bold"),

            dropdown_db,

            ft.Row([
                ruta_carpeta,
                ft.IconButton(
                    icon=ft.Icons.FOLDER_OPEN,
                    tooltip="Seleccionar carpeta",
                    on_click=seleccionar_carpeta
                )
            ]),

            nombre_archivo,

            ft.Row([
                ft.ElevatedButton("Crear Backup", on_click=backup),
                ft.ElevatedButton("Restaurar Backup", on_click=restaurar)
            ])
        ]
    )