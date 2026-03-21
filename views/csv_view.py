import flet as ft
from services.csv_service import exportar_csv, importar_csv
from services.db_service import obtener_bases
from services.table_service import obtener_tablas

import tkinter as tk
from tkinter import filedialog
import threading
import os


def csv_view(page: ft.Page):

    dropdown_db = ft.Dropdown(label="Base de datos", width=250)
    dropdown_tabla = ft.Dropdown(label="Tabla", width=250)

    ruta_archivo = ft.TextField(label="Archivo CSV", width=400, read_only=True)

    nombre_export = ft.TextField(label="Nombre archivo export", width=250)

    # 🔄 cargar bases
    def cargar_bases():
        bases = obtener_bases()
        dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
        page.update()

    # 🔄 cargar tablas
    def cargar_tablas(e=None):
        db = dropdown_db.value
        if not db:
            return

        tablas = obtener_tablas(db)
        dropdown_tabla.options = [ft.dropdown.Option(t) for t in tablas]
        page.update()

    # 📂 seleccionar archivo
    def seleccionar_archivo(e):

        def abrir():
            root = tk.Tk()
            root.withdraw()

            archivo = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv")]
            )

            if archivo:
                ruta_archivo.value = archivo
                page.update()

            root.destroy()

        threading.Thread(target=abrir).start()

    # 📂 seleccionar carpeta export
    def seleccionar_carpeta(e):

        def abrir():
            root = tk.Tk()
            root.withdraw()

            carpeta = filedialog.askdirectory()

            if carpeta:
                ruta_archivo.value = carpeta
                page.update()

            root.destroy()

        threading.Thread(target=abrir).start()

    # 📤 EXPORTAR
    def exportar(e):
        db = dropdown_db.value
        tabla = dropdown_tabla.value
        ruta = ruta_archivo.value
        nombre = nombre_export.value

        if not db or not tabla or not ruta or not nombre:
            mostrar("Completa todos los campos")
            return

        ruta_final = os.path.join(ruta, f"{nombre}.csv")

        ok = exportar_csv(db, tabla, ruta_final)

        if ok:
            mostrar(f"Exportado correctamente ✅\n{ruta_final}")
        else:
            mostrar("Error al exportar ❌")

    # 📥 IMPORTAR
    def importar(e):
        db = dropdown_db.value
        tabla = dropdown_tabla.value
        archivo = ruta_archivo.value

        if not db or not tabla or not archivo:
            mostrar("Completa todos los campos")
            return

        ok = importar_csv(db, tabla, archivo)

        if ok:
            mostrar("Importado correctamente ✅")
        else:
            mostrar("Error al importar ❌")

    # 🔔 mensajes
    def mostrar(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    dropdown_db.on_change = cargar_tablas

    cargar_bases()

    return ft.Column(
        [
            ft.Text("📄 Importar / Exportar CSV", size=24, weight="bold"),

            dropdown_db,
            dropdown_tabla,

            ft.Divider(),

            ft.Text("Exportar:", weight="bold"),

            ft.Row([
                ruta_archivo,
                ft.IconButton(
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=seleccionar_carpeta
                )
            ]),

            nombre_export,
            ft.ElevatedButton("Exportar CSV", on_click=exportar),

            ft.Divider(),

            ft.Text("Importar:", weight="bold"),

            ft.Row([
                ruta_archivo,
                ft.IconButton(
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=seleccionar_archivo
                )
            ]),

            ft.ElevatedButton("Importar CSV", on_click=importar)
        ]
    )