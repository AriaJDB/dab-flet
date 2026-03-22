import flet as ft
from services.csv_service import exportar_csv, importar_csv
from services.db_service import obtener_bases
from services.table_service import obtener_tablas

import tkinter as tk
from tkinter import filedialog
import threading
import os

def csv_view(page: ft.Page):
    # --- Controles de Selección ---
    dropdown_db = ft.Dropdown(
        label="Seleccionar Base de Datos",
        width=350,
        border_radius=10,
    )
    
    dropdown_tabla = ft.Dropdown(
        label="Seleccionar Tabla",
        width=350,
        border_radius=10,
    )

    # --- Inputs de Archivos ---
    ruta_archivo = ft.TextField(
        label="Ruta Seleccionada",
        hint_text="Usa los iconos para buscar...",
        width=450,
        read_only=True,
        border_radius=10,
        bgcolor=ft.Colors.GREY_50
    )

    nombre_export = ft.TextField(
        label="Nombre del archivo final",
        hint_text="Ej: reporte_ventas",
        width=350,
        border_radius=10
    )

    # ✅ Asignación de eventos fuera del constructor
    def on_db_change(e):
        cargar_tablas()

    dropdown_db.on_change = on_db_change

    # 🔄 Lógica de datos
    def cargar_bases():
        try:
            bases = obtener_bases()
            dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
            page.update()
        except Exception as e:
            mostrar(f"Error al conectar: {e}")

    def cargar_tablas():
        db = dropdown_db.value
        if not db: return
        try:
            tablas = obtener_tablas(db)
            dropdown_tabla.options = [ft.dropdown.Option(t) for t in tablas]
            page.update()
        except Exception as e:
            mostrar(f"Error tablas: {e}")

    # 📂 Lógica de archivos con Tkinter en hilo separado
    def seleccionar_archivo(e):
        def abrir():
            root = tk.Tk()
            root.withdraw()
            archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if archivo:
                ruta_archivo.value = archivo
                page.update()
            root.destroy()
        threading.Thread(target=abrir, daemon=True).start()

    def seleccionar_carpeta(e):
        def abrir():
            root = tk.Tk()
            root.withdraw()
            carpeta = filedialog.askdirectory()
            if carpeta:
                ruta_archivo.value = carpeta
                page.update()
            root.destroy()
        threading.Thread(target=abrir, daemon=True).start()

    # 📤 Procesos
    def exportar(e):
        db = dropdown_db.value
        tabla = dropdown_tabla.value
        ruta = ruta_archivo.value
        nombre = nombre_export.value

        if not all([db, tabla, ruta, nombre]):
            mostrar("Por favor, completa todos los campos de exportación")
            return

        ruta_final = os.path.join(ruta, f"{nombre}.csv")
        if exportar_csv(db, tabla, ruta_final):
            mostrar(f"¡Exportación exitosa! ✅\nUbicación: {ruta_final}")
        else:
            mostrar("Error en el proceso de exportación ❌")

    def importar(e):
        db = dropdown_db.value
        tabla = dropdown_tabla.value
        archivo = ruta_archivo.value

        if not all([db, tabla, archivo]):
            mostrar("Selecciona DB, Tabla y Archivo CSV")
            return

        if importar_csv(db, tabla, archivo):
            mostrar("Datos importados correctamente ✅")
        else:
            mostrar("Error al procesar el archivo CSV ❌")

    def mostrar(msg):
        # Forma moderna de mostrar SnackBar en 0.80+
        page.open(ft.SnackBar(ft.Text(msg)))

    cargar_bases()

    # --- DISEÑO FINAL PROFESIONAL ---
    return ft.Column([
        # Título
        ft.Row([
            ft.Column([
                ft.Text("Intercambio de Datos", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Mueve información entre CSV y tu Base de Datos", color=ft.Colors.BLUE_GREY_400),
            ])
        ]),

        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

        # Paso 1: Configuración de Base de Datos
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SETTINGS_ETHERNET_ROUNDED, color=ft.Colors.BLUE_700),
                dropdown_db,
                ft.Icon(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, size=15, color=ft.Colors.GREY_400),
                dropdown_tabla,
            ], alignment=ft.MainAxisAlignment.START, spacing=20),
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        ),

        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

        # Paso 2: Importar / Exportar Cards
        ft.Row([
            # CARD EXPORTAR (Azul suave)
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, color=ft.Colors.BLUE_800), ft.Text("Exportar a CSV", size=18, weight="bold")]),
                    ft.Text("Guarda una tabla en tu computadora.", color=ft.Colors.BLUE_GREY_600),
                    ft.Divider(),
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER_OPEN_ROUNDED, size=20),
                        ft.Text("Destino:", weight="bold"),
                    ]),
                    ft.Row([ruta_archivo, ft.IconButton(icon=ft.Icons.SEARCH, on_click=seleccionar_carpeta, bgcolor=ft.Colors.BLUE_50)]),
                    nombre_export,
                    ft.Button(
                        "Iniciar Exportación", 
                        icon=ft.Icons.PLAY_ARROW_ROUNDED, 
                        on_click=exportar,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
                    ),
                ], spacing=15),
                expand=True,
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                border=ft.Border(top=ft.BorderSide(5, ft.Colors.BLUE_700)),
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
            ),

            # CARD IMPORTAR (Verde suave)
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.UPLOAD_ROUNDED, color=ft.Colors.GREEN_800), ft.Text("Importar desde CSV", size=18, weight="bold")]),
                    ft.Text("Carga datos externos a una tabla.", color=ft.Colors.BLUE_GREY_600),
                    ft.Divider(),
                    ft.Row([
                        ft.Icon(ft.Icons.FILE_UPLOAD_OUTLINED, size=20),
                        ft.Text("Archivo:", weight="bold"),
                    ]),
                    ft.Row([ruta_archivo, ft.IconButton(icon=ft.Icons.ATTACH_FILE_ROUNDED, on_click=seleccionar_archivo, bgcolor=ft.Colors.GREEN_50)]),
                    ft.Divider(height=45, color=ft.Colors.TRANSPARENT), # Espaciador para alinear botones
                    ft.Button(
                        "Iniciar Importación", 
                        icon=ft.Icons.CLOUD_UPLOAD_ROUNDED, 
                        on_click=importar,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
                    ),
                ], spacing=15),
                expand=True,
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                border=ft.Border(top=ft.BorderSide(5, ft.Colors.GREEN_700)),
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
            ),
        ], expand=True, spacing=20)
    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)