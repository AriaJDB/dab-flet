import flet as ft
from services.backup_service import hacer_backup, restaurar_backup
from services.db_service import obtener_bases
import os
import tkinter as tk
from tkinter import filedialog
import threading

def backup_view(page: ft.Page):

    # --- Elemento de Mensaje Fijo Estilizado ---
    txt_mensaje = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    msg_container = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.INFO_OUTLINE, size=20), txt_mensaje], spacing=10),
        padding=10,
        border_radius=8,
        visible=False # Se oculta hasta que haya un mensaje
    )
    
    def mostrar_alerta(msg, es_error=True):
        txt_mensaje.value = msg
        msg_container.visible = True
        if es_error:
            msg_container.bgcolor = ft.Colors.RED_50
            txt_mensaje.color = ft.Colors.RED_700
            msg_container.content.controls[0].color = ft.Colors.RED_700
            msg_container.content.controls[0].name = ft.Icons.ERROR_OUTLINE
        else:
            msg_container.bgcolor = ft.Colors.GREEN_50
            txt_mensaje.color = ft.Colors.GREEN_700
            msg_container.content.controls[0].color = ft.Colors.GREEN_700
            msg_container.content.controls[0].name = ft.Icons.CHECK_CIRCLE_OUTLINE
        page.update()

    # --- Controles de Formulario ---
    dropdown_db = ft.Dropdown(label="Base de Datos", width=400, border_radius=10)
    ruta_carpeta = ft.TextField(label="Carpeta de Destino", width=450, read_only=True, border_radius=10)
    nombre_archivo = ft.TextField(label="Nombre del Backup", width=400, border_radius=10, prefix_icon=ft.Icons.DESCRIPTION)

    # 🔄 Cargar bases
    def cargar_bases():
        try:
            bases = obtener_bases()
            dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
            page.update()
        except Exception as e:
            mostrar_alerta(f"Error al conectar con MariaDB: {e}")

    # 📂 Explorador (Corregido para salir al frente)
    def seleccionar_ruta(e):
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

    # 💾 Lógica de Ejecución
    def ejecutar_accion(tipo):
        if not all([dropdown_db.value, ruta_carpeta.value, nombre_archivo.value]):
            mostrar_alerta("❌ Por favor, completa todos los campos antes de continuar.")
            return
        
        ruta_final = os.path.join(ruta_carpeta.value, f"{nombre_archivo.value}.sql")
        mostrar_alerta("⏳ Procesando... Por favor espera.", es_error=False)
        msg_container.bgcolor = ft.Colors.BLUE_50
        txt_mensaje.color = ft.Colors.BLUE_700
        page.update()

        try:
            if tipo == "backup":
                ok = hacer_backup(dropdown_db.value, "root", "latte", ruta_final)
                msg_exito = f"✅ Respaldo creado exitosamente en {nombre_archivo.value}.sql"
            else:
                ok = restaurar_backup(dropdown_db.value, "root", "latte", ruta_final)
                msg_exito = "✅ Base de datos restaurada correctamente."
            
            if ok:
                mostrar_alerta(msg_exito, es_error=False)
            else:
                mostrar_alerta("❌ El sistema no pudo completar la operación. Revisa los permisos.")
        except Exception as ex:
            mostrar_alerta(f"🔥 Error del Sistema: {ex}")

    cargar_bases()

    # --- DISEÑO FINAL ---
    return ft.Column([
        # Título y Mensajes
        ft.Column([
            ft.Text("Respaldo y Recuperación", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Gestión de seguridad de datos SQL", color=ft.Colors.BLUE_GREY_400),
            msg_container, # El mensaje ahora vive aquí arriba
        ]),

        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

        # Card de Configuración
        ft.Container(
            content=ft.Column([
                ft.Text("Configuración de Ruta", weight=ft.FontWeight.BOLD, size=16),
                dropdown_db,
                ft.Row([
                    ruta_carpeta,
                    ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_color=ft.Colors.BLUE_700, on_click=seleccionar_ruta)
                ]),
                nombre_archivo,
            ], spacing=20),
            padding=30,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        ),

        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

        # Tarjetas de Acción (Restauradas)
        ft.Row([
            # Card Crear Backup
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CLOUD_DONE_ROUNDED, color=ft.Colors.BLUE_700, size=40),
                    ft.Text("Generar Backup", weight="bold"),
                    ft.Text("Crea una copia de seguridad.", size=12, text_align=ft.TextAlign.CENTER),
                    ft.Button(
                        "Respaldar Ahora",
                        on_click=lambda _: ejecutar_accion("backup"),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                expand=True, padding=20, bgcolor=ft.Colors.BLUE_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.WHITE10, border_radius=15
            ),

            # Card Restaurar
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY_ROUNDED, color=ft.Colors.AMBER_800, size=40),
                    ft.Text("Restaurar Base", weight="bold"),
                    ft.Text("Sobreescribe con un archivo .sql", size=12, text_align=ft.TextAlign.CENTER),
                    ft.Button(
                        "Restaurar Ahora",
                        on_click=lambda _: ejecutar_accion("restore"),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_800, color=ft.Colors.WHITE)
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                expand=True, padding=20, bgcolor=ft.Colors.AMBER_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.WHITE10, border_radius=15
            )
        ], spacing=20)
    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)