import flet as ft

# 🔐 login
from views.login_view import login_view

# 📦 vistas
from views.db_view import db_view
from views.table_view import table_view
from views.csv_view import csv_view
from views.backup_view import backup_view
from views.user_view import user_view
from views.metrics_view import metrics_view

def main(page: ft.Page):
    # Configuración inicial de la ventana
    page.title = "DB Manager Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1100
    page.window_height = 750
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 0

    # 🧠 Estado global
    usuario_actual = {"user": None, "permisos": ""}

    # --- Contenedores Principales ---
    # Este contenedor alojará las vistas que importas (db_view, table_view, etc.)
    content_area = ft.Container(
        expand=True,
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.BorderRadius(30, 0, 0, 0), # Esquina superior izquierda redondeada
        padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
        content=ft.Column([ft.Text("Cargando Dashboard...")])
    )

    sidebar_items = ft.Column(spacing=5, scroll=ft.ScrollMode.ADAPTIVE)

    # --- Función para crear botones del menú con estilo profesional ---
    def sidebar_button(text, icon, view_name):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=ft.Colors.BLUE_GREY_400),
                ft.Text(text, color=ft.Colors.BLUE_GREY_700, weight=ft.FontWeight.W_500)
            ]),
            padding=ft.Padding.all(12),
            border_radius=ft.BorderRadius.all(10),
            on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.BLACK12 if e.data == "true" else None) or e.control.update(),
            on_click=lambda _: cargar_vista(view_name),
        )

    # 🔄 Lógica para intercambiar las vistas importadas
    def cargar_vista(nombre):
        content_area.content = ft.Column([ft.ProgressRing()], alignment=ft.MainAxisAlignment.CENTER)
        page.update()

        # Selección de vista según el nombre
        if nombre == "db":
            nueva_vista = db_view(page)
        elif nombre == "tables":
            nueva_vista = table_view(page)
        elif nombre == "csv":
            nueva_vista = csv_view(page)
        elif nombre == "backup":
            nueva_vista = backup_view(page)
        elif nombre == "users":
            nueva_vista = user_view(page)
        elif nombre == "metrics":
            nueva_vista = metrics_view(page)
        else:
            nueva_vista = ft.Text("Vista no encontrada")

        content_area.content = nueva_vista
        page.update()

    # 🧱 Construcción del Layout Principal (Dashboard)
    def mostrar_menu():
        page.controls.clear()
        sidebar_items.controls.clear()

        permisos = usuario_actual["permisos"]

        # Header del Menú (Usuario)
        sidebar_items.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE_ROUNDED, size=40, color=ft.Colors.BLUE_700),
                    ft.Column([
                        ft.Text(usuario_actual['user'], weight=ft.FontWeight.BOLD, size=16),
                        ft.Text("Administrador" if "ALL" in permisos else "Operador", size=12, color=ft.Colors.BLUE_GREY_400)
                    ], spacing=0)
                ]),
                padding=ft.Padding.only(bottom=20)
            )
        )

        # Filtro de Menú basado en tus privilegios originales
        if "ALL PRIVILEGES" in permisos:
            sidebar_items.controls.extend([
                sidebar_button("Bases de Datos", ft.Icons.STORAGE_ROUNDED, "db"),
                sidebar_button("Tablas", ft.Icons.TABLE_CHART_ROUNDED, "tables"),
                sidebar_button("Importar CSV", ft.Icons.FILE_OPEN_ROUNDED, "csv"),
                sidebar_button("Backups", ft.Icons.BACKUP_ROUNDED, "backup"),
                sidebar_button("Usuarios", ft.Icons.PEOPLE_ALT_ROUNDED, "users"),
                sidebar_button("Métricas", ft.Icons.INSERT_CHART_ROUNDED, "metrics"),
            ])
        else:
            if "SELECT" in permisos:
                sidebar_items.controls.append(sidebar_button("Ver Tablas", ft.Icons.VIEW_LIST_ROUNDED, "tables"))
            if "INSERT" in permisos:
                sidebar_items.controls.append(sidebar_button("Insertar Datos", ft.Icons.ADD_BOX_ROUNDED, "tables"))

        # Botón para salir
        sidebar_items.controls.append(ft.Divider(height=30, color=ft.Colors.TRANSPARENT))
        sidebar_items.controls.append(
            ft.Button(
                "Cerrar Sesión", 
                icon=ft.Icons.LOGOUT_ROUNDED, 
                on_click=lambda _: ir_a_login(),
                style=ft.ButtonStyle(color=ft.Colors.RED_400)
            )
        )

        # Ensamblaje final del Dashboard
        layout = ft.Row(
            [
                ft.Container(sidebar_items, width=250, padding=20),
                content_area
            ],
            expand=True,
            spacing=0
        )
        
        page.add(layout)
        # Cargar la primera vista por defecto
        cargar_vista("db" if "ALL" in permisos else "tables")

    # 🔐 Lógica de Login
    def on_login(user, permisos):
        usuario_actual["user"] = user
        usuario_actual["permisos"] = permisos
        mostrar_menu()

    def ir_a_login():
        page.controls.clear()
        # Llamada a tu vista de login original
        # Asegúrate de que login_view acepte (page, on_login) como argumentos
        page.add(
            ft.Container(
                content=login_view(page, on_login),
                expand=True,
                alignment=ft.Alignment.CENTER
            )
        )
        page.update()

    # 🚀 Iniciar App
    ir_a_login()

# ▶️ Ejecutar
if __name__ == "__main__":
    ft.run(main)