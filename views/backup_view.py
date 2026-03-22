import flet as ft
from services.backup_service import hacer_backup, restaurar_backup
from services.db_service import obtener_bases
import os
import tkinter as tk
from tkinter import filedialog
import threading

def backup_view(page: ft.Page):
    # --- Controles de Formulario ---
    dropdown_db = ft.Dropdown(
        label="Base de Datos a procesar",
        width=400,
        border_radius=10,
        hint_text="Selecciona la base de datos destino/origen"
    )

    ruta_carpeta = ft.TextField(
        label="Ubicación del Archivo (.sql)",
        hint_text="Haz clic en la carpeta para buscar...",
        width=450,
        read_only=True,
        border_radius=10,
        bgcolor=ft.Colors.GREY_50
    )

    nombre_archivo = ft.TextField(
        label="Nombre del Backup",
        hint_text="Ej: respaldo_nomina_marzo",
        width=400,
        border_radius=10,
        prefix_icon=ft.Icons.DESCRIPTION_OUTLINED # Un icono de archivo
    )

    # 🔄 Cargar bases
    def cargar_bases():
        try:
            bases = obtener_bases()
            dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
            page.update()
        except Exception as e:
            notificar(f"Error al cargar bases: {e}")

    # 📂 Explorador (Tkinter en hilo para evitar congelamientos)
    def seleccionar_ruta(e):
        def abrir():
            root = tk.Tk()
            root.withdraw()
            # Si es para restaurar, quizá prefieras askopenfilename, 
            # pero mantendremos tu lógica de carpeta + nombre manual
            ruta = filedialog.askdirectory()
            if ruta:
                ruta_carpeta.value = ruta
                page.update()
            root.destroy()
        threading.Thread(target=abrir, daemon=True).start()

    # 💾 Lógica de procesos
    def ejecutar_backup(e):
        if not validar(): return
        
        ruta_final = os.path.join(ruta_carpeta.value, f"{nombre_archivo.value}.sql")
        # Nota: He mantenido tus credenciales hardcoded pero te sugiero variables de entorno en el futuro
        ok = hacer_backup(dropdown_db.value, "root", "latte", ruta_final)
        
        if ok:
            notificar(f"Respaldo generado en: {ruta_final} ✅")
        else:
            notificar("Error crítico al generar respaldo ❌")

    def ejecutar_restauracion(e):
        if not validar(): return
        
        ruta_final = os.path.join(ruta_carpeta.value, f"{nombre_archivo.value}.sql")
        # Aquí podrías añadir un Dialog de confirmación antes de restaurar
        ok = restaurar_backup(dropdown_db.value, "root", "latte", ruta_final)
        
        if ok:
            notificar("¡Base de datos restaurada con éxito! ✅")
        else:
            notificar("Error al restaurar el archivo SQL ❌")

    def validar():
        if not all([dropdown_db.value, ruta_carpeta.value, nombre_archivo.value]):
            notificar("Por favor, completa todos los campos de seguridad")
            return False
        return True

    def notificar(msg):
        page.open(ft.SnackBar(ft.Text(msg)))

    cargar_bases()

    # --- DISEÑO VISUAL ---
    return ft.Column([
        # Título
        ft.Row([
            ft.Column([
                ft.Text("Respaldo y Recuperación", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Administra la persistencia de seguridad de tus datos", color=ft.Colors.BLUE_GREY_400),
            ])
        ]),

        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

        # Card de Configuración de Archivo
        ft.Container(
            content=ft.Column([
                ft.Text("Configuración de Ruta", weight=ft.FontWeight.BOLD, size=16),
                dropdown_db,
                ft.Row([
                    ruta_carpeta,
                    ft.IconButton(
                        icon=ft.Icons.FOLDER_SPECIAL_ROUNDED,
                        icon_size=30,
                        icon_color=ft.Colors.BLUE_700,
                        on_click=seleccionar_ruta,
                        tooltip="Explorar carpetas"
                    )
                ]),
                nombre_archivo,
            ], spacing=20),
            padding=30,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        ),

        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

        # Fila de Acciones con advertencias visuales
        ft.Row([
            # Card Crear
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CLOUD_DONE_ROUNDED, color=ft.Colors.BLUE_700, size=40),
                    ft.Text("Generar Backup", weight="bold"),
                    ft.Text("Crea una copia exacta actual.", size=12, text_align=ft.TextAlign.CENTER),
                    ft.Button(
                        "Respaldar Ahora",
                        on_click=ejecutar_backup,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                expand=True, padding=20, bgcolor=ft.Colors.BLUE_50, border_radius=15
            ),

            # Card Restaurar (Peligro)
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY_ROUNDED, color=ft.Colors.AMBER_800, size=40),
                    ft.Text("Restaurar Datos", weight="bold"),
                    ft.Text("Sobreescribe la base actual.", size=12, text_align=ft.TextAlign.CENTER),
                    ft.Button(
                        "Restaurar Base",
                        on_click=ejecutar_restauracion,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_800, color=ft.Colors.WHITE)
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                expand=True, padding=20, bgcolor=ft.Colors.AMBER_50, border_radius=15
            )
        ], spacing=20)
    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)