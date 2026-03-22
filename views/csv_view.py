import flet as ft
from services.csv_service import exportar_csv, importar_csv
from services.db_service import obtener_bases
from services.table_service import obtener_tablas
import tkinter as tk
from tkinter import filedialog
import threading
import os

def csv_view(page: ft.Page):
    # --- Colores Reactivos ---
    # Estos colores cambian automáticamente según el tema de la página
    bg_color = ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE
    card_shadow = ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
    
    # --- UI Estática de Mensajes ---
    txt_mensaje = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    msg_container = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.INFO_OUTLINE, size=20), txt_mensaje], spacing=10),
        padding=10, border_radius=8, visible=False, margin=ft.margin.only(bottom=10)
    )

    def mostrar_alerta(msg, es_error=True):
        txt_mensaje.value = msg
        msg_container.visible = True
        # Colores de alerta adaptados para modo oscuro/claro
        if es_error:
            msg_container.bgcolor = ft.Colors.RED_900 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.RED_50
            txt_mensaje.color = ft.Colors.RED_100 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.RED_700
        else:
            msg_container.bgcolor = ft.Colors.BLUE_900 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_50
            txt_mensaje.color = ft.Colors.BLUE_100 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_700
        page.update()

    # --- Controles de Selección ---
    dropdown_db = ft.Dropdown(label="Seleccionar Base de Datos", width=350, border_radius=10)
    container_tabla = ft.Container()

    def obtener_dropdown_tabla(opciones=[]):
        return ft.Dropdown(
            label="Seleccionar Tabla",
            width=350,
            border_radius=10,
            options=[ft.dropdown.Option(t) for t in opciones]
        )

    container_tabla.content = obtener_dropdown_tabla()

    ruta_export = ft.TextField(label="Carpeta de destino", read_only=True, expand=True, border_radius=10)
    ruta_import = ft.TextField(label="Archivo .csv", read_only=True, expand=True, border_radius=10)
    nombre_export = ft.TextField(label="Nombre del archivo final", width=350, border_radius=10)

    # 🔄 Lógica de carga de tablas
    def cargar_tablas(e):
        db = dropdown_db.value
        if not db: return
        try:
            tablas = obtener_tablas(db)
            container_tabla.content = obtener_dropdown_tabla(tablas)
            container_tabla.update() 
            mostrar_alerta(f"Tablas de '{db}' cargadas correctamente", False)
        except Exception as ex:
            mostrar_alerta(f"Error: {ex}")

    def cargar_bases():
        try:
            bases = obtener_bases()
            dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
            page.update()
        except Exception as e:
            mostrar_alerta(f"Error conexión: {e}")

    dropdown_db.on_change = cargar_tablas

    # 📂 Lógica de exploradores
    def seleccionar_path(tipo):
        def abrir():
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            if tipo == "carpeta":
                res = filedialog.askdirectory()
                if res: ruta_export.value = res
            else:
                res = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
                if res: ruta_import.value = res
            page.update()
            root.destroy()
        threading.Thread(target=abrir, daemon=True).start()

    # 📤 Procesos
    def ejecutar_exportar(e):
        tabla_val = container_tabla.content.value
        if not all([dropdown_db.value, tabla_val, ruta_export.value, nombre_export.value]):
            mostrar_alerta("Faltan datos para exportar")
            return
        path = os.path.join(ruta_export.value, f"{nombre_export.value}.csv")
        if exportar_csv(dropdown_db.value, tabla_val, path):
            mostrar_alerta("Exportación exitosa ✅", False)
        else:
            mostrar_alerta("Error al exportar")

    def ejecutar_importar(e):
        tabla_val = container_tabla.content.value
        if not all([dropdown_db.value, tabla_val, ruta_import.value]):
            mostrar_alerta("Faltan datos para importar")
            return
        if importar_csv(dropdown_db.value, tabla_val, ruta_import.value):
            mostrar_alerta("Importación exitosa ✅", False)
        else:
            mostrar_alerta("Error al importar CSV")

    cargar_bases()

    return ft.Column([
        ft.Text("Intercambio de Datos (CSV)", size=28, weight="bold"),
        ft.Text("Importación y exportación de datos CSV", color=ft.Colors.BLUE_GREY_400),
        msg_container,
        
        # PASO 1: Selección Global
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.STORAGE_ROUNDED, color=ft.Colors.BLUE_700),
                dropdown_db,
                ft.Icon(ft.Icons.ARROW_FORWARD, size=15, color=ft.Colors.GREY_400),
                container_tabla,
            ], spacing=20),
            padding=20, 
            bgcolor=bg_color, # Color Adaptativo
            border_radius=15,
            shadow=card_shadow
        ),

        ft.Row([
            # CARD EXPORTAR
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.FILE_DOWNLOAD, color=ft.Colors.BLUE_800), ft.Text("Exportar", weight="bold")]),
                    ft.Divider(),
                    ft.Row([
                        ruta_export, 
                        ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_color=ft.Colors.BLUE_700, on_click=lambda _: seleccionar_path("carpeta"))
                    ]),
                    nombre_export,
                    ft.ElevatedButton("Exportar CSV", on_click=ejecutar_exportar, bgcolor=ft.Colors.BLUE_700, color="white")
                ], spacing=15),
                expand=True, padding=25, bgcolor=bg_color, border_radius=15,
                border=ft.Border(top=ft.BorderSide(5, ft.Colors.BLUE_700)),
                shadow=card_shadow
            ),

            # CARD IMPORTAR
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.FILE_UPLOAD, color=ft.Colors.GREEN_800), ft.Text("Importar", weight="bold")]),
                    ft.Divider(),
                    ft.Row([
                        ruta_import, 
                        ft.IconButton(icon=ft.Icons.ATTACH_FILE, icon_color=ft.Colors.GREEN_700, on_click=lambda _: seleccionar_path("archivo"))
                    ]),
                    ft.Divider(height=45, color=ft.Colors.TRANSPARENT),
                    ft.ElevatedButton("Importar CSV", on_click=ejecutar_importar, bgcolor=ft.Colors.GREEN_700, color="white")
                ], spacing=15),
                expand=True, padding=25, bgcolor=bg_color, border_radius=15,
                border=ft.Border(top=ft.BorderSide(5, ft.Colors.GREEN_700)),
                shadow=card_shadow
            ),
        ], spacing=20)
    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)