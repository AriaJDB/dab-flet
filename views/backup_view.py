import flet as ft
from services.backup_service import hacer_backup, restaurar_backup
from services.db_service import obtener_bases
import os
import tkinter as tk
from tkinter import filedialog
import threading
from datetime import datetime

def backup_view(page: ft.Page):

    # --- MENSAJES ---
    txt_mensaje = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    icono_msg = ft.Icon(ft.Icons.INFO_OUTLINE, size=20)

    msg_container = ft.Container(
        content=ft.Row([icono_msg, txt_mensaje], spacing=10),
        padding=10,
        border_radius=8,
        visible=False
    )
    
    def mostrar_alerta(msg, es_error=True):
        txt_mensaje.value = msg
        msg_container.visible = True

        if es_error:
            msg_container.bgcolor = ft.Colors.RED_50
            txt_mensaje.color = ft.Colors.RED_700
            icono_msg.name = ft.Icons.ERROR_OUTLINE
            icono_msg.color = ft.Colors.RED_700
        else:
            msg_container.bgcolor = ft.Colors.GREEN_50
            txt_mensaje.color = ft.Colors.GREEN_700
            icono_msg.name = ft.Icons.CHECK_CIRCLE_OUTLINE
            icono_msg.color = ft.Colors.GREEN_700

        page.update()

    # --- CONTROLES ---
    dropdown_db = ft.Dropdown(label="Base de Datos", width=400, border_radius=10)

    ruta_carpeta = ft.TextField(label="Carpeta de destino", read_only=True, expand=True, border_radius=10)
    nombre_archivo = ft.TextField(label="Nombre del backup", width=300, border_radius=10)

    usar_nombre = ft.Checkbox(label="Usar nombre personalizado", value=False)

    ruta_archivo_restore = ft.TextField(label="Archivo .sql", read_only=True, expand=True, border_radius=10)

    # --- CARGAR BASES ---
    def cargar_bases():
        try:
            bases = obtener_bases()
            dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
            page.update()
        except Exception as e:
            mostrar_alerta(f"Error al conectar: {e}")

    # --- SELECTORES ---
    def seleccionar_carpeta():
        def abrir():
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            ruta = filedialog.askdirectory()
            if ruta:
                ruta_carpeta.value = ruta
                page.update()
            root.destroy()
        threading.Thread(target=abrir, daemon=True).start()

    def seleccionar_archivo():
        def abrir():
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            archivo = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql")])
            if archivo:
                ruta_archivo_restore.value = archivo
                page.update()
            root.destroy()
        threading.Thread(target=abrir, daemon=True).start()

    # --- HABILITAR INPUT ---
    def toggle_nombre(e):
        nombre_archivo.disabled = not usar_nombre.value
        page.update()

    usar_nombre.on_change = toggle_nombre
    nombre_archivo.disabled = True

    # --- GENERAR NOMBRE AUTOMÁTICO ---
    def generar_nombre_auto(db):
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{db}_backup_{fecha}"

    # --- ACCIONES ---
    def ejecutar_backup(e):
        if not dropdown_db.value or not ruta_carpeta.value:
            mostrar_alerta("Selecciona base y carpeta")
            return

        if usar_nombre.value:
            if not nombre_archivo.value:
                mostrar_alerta("Ingresa un nombre")
                return
            if " " in nombre_archivo.value:
                mostrar_alerta("El nombre no puede tener espacios")
                return
            nombre = nombre_archivo.value
        else:
            nombre = generar_nombre_auto(dropdown_db.value)

        ruta_final = os.path.join(ruta_carpeta.value, f"{nombre}.sql")

        try:
            ok = hacer_backup(dropdown_db.value, "root", "latte", ruta_final)
            if ok:
                mostrar_alerta(f"Backup creado: {nombre}.sql", False)
            else:
                mostrar_alerta("No se pudo crear el backup")
        except Exception as ex:
            mostrar_alerta(f"Error: {ex}")

    def ejecutar_restore(e):
        if not dropdown_db.value or not ruta_archivo_restore.value:
            mostrar_alerta("Selecciona base y archivo")
            return

        try:
            ok = restaurar_backup(dropdown_db.value, "root", "latte", ruta_archivo_restore.value)
            if ok:
                mostrar_alerta("Base restaurada correctamente", False)
            else:
                mostrar_alerta("No se pudo restaurar")
        except Exception as ex:
            mostrar_alerta(f"Error: {ex}")

    cargar_bases()

    # --- UI ---
    return ft.Column([

        ft.Column([
            ft.Text("Respaldo y Recuperación", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Gestión de seguridad de datos SQL", color=ft.Colors.BLUE_GREY_400),
            msg_container,
        ]),

        ft.Container(
            content=dropdown_db,
            padding=20,
            border_radius=15,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE
        ),

        ft.Row([

            # --- BACKUP ---
            ft.Container(
                height=360,
                content=ft.Column([
                    ft.Icon(ft.Icons.CLOUD_DONE_ROUNDED, color=ft.Colors.BLUE_700, size=40),
                    ft.Text("Generar Backup", weight="bold"),
                    ft.Text("Crea una copia de seguridad.", size=12),

                    ft.Row([
                        ruta_carpeta,
                        ft.IconButton(icon=ft.Icons.FOLDER_OPEN, on_click=lambda _: seleccionar_carpeta())
                    ]),

                    usar_nombre,
                    nombre_archivo,

                    ft.Button(
                        "Respaldar Ahora",
                        on_click=ejecutar_backup,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
                    )
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                expand=True,
                padding=20,
                bgcolor=ft.Colors.BLUE_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.WHITE10,
                border_radius=15
            ),

            # --- RESTORE ---
            ft.Container(
                height=360,
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY_ROUNDED, color=ft.Colors.AMBER_800, size=40),
                    ft.Text("Restaurar Base", weight="bold"),
                    ft.Text("Sobreescribe con un archivo .sql", size=12),

                    ft.Row([
                        ruta_archivo_restore,
                        ft.IconButton(icon=ft.Icons.ATTACH_FILE, on_click=lambda _: seleccionar_archivo())
                    ]),

                    ft.Button(
                        "Restaurar Ahora",
                        on_click=ejecutar_restore,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_800, color=ft.Colors.WHITE)
                    )
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                expand=True,
                padding=20,
                bgcolor=ft.Colors.AMBER_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.WHITE10,
                border_radius=15
            )

        ], spacing=20)

    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)