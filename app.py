import flet as ft
from views.login_view import login_view
from views.db_view import db_view
from views.csv_view import csv_view
from views.backup_view import backup_view
from views.user_view import user_view
from views.metrics_view import metrics_view
from views.query_view import query_view

def main(page: ft.Page):
    page.title = "LatteDB Manager"

    def maximizar():
        page.window_maximized = True
        page.update()

    page.on_connect = lambda e: maximizar()

    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_maximized = True
    page.window_resizable = True
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 0

    page.session_data = {"user": None, "permisos": ""}

    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_400,
            surface=ft.Colors.BLUE_GREY_900,
            on_surface=ft.Colors.GREY_100,
        ),
    )
    
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_700,
            surface=ft.Colors.WHITE,
            on_surface=ft.Colors.BLACK,
        ),
    )

    def notificar(mensaje, color=ft.Colors.RED_700):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=color,
            show_close_icon=True,
        )
        page.snack_bar.open = True
        page.update()

    page.notificar = notificar

    content_area = ft.Container(
        expand=True,
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.BorderRadius(30, 0, 0, 0),
        padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
        content=ft.Column([ft.Text("Cargando...")])
    )

    sidebar_items = ft.Column(spacing=5, scroll=ft.ScrollMode.ADAPTIVE)

    def cambiar_tema(e):
        page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        
        if page.theme_mode == ft.ThemeMode.DARK:
            page.bgcolor = ft.Colors.BLUE_GREY_900
            content_area.bgcolor = "#1e1e26"
        else:
            page.bgcolor = ft.Colors.BLUE_GREY_50
            content_area.bgcolor = ft.Colors.WHITE
        
        page.update()

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

    def cargar_vista(nombre):
        content_area.content = ft.Column([ft.ProgressRing()], alignment=ft.MainAxisAlignment.CENTER)
        page.update()

        if nombre == "db":
            nueva_vista = db_view(page, page.session_data)
        elif nombre == "query":
            nueva_vista = query_view(page)
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

    def mostrar_menu():
        page.controls.clear()
        sidebar_items.controls.clear()
        permisos = page.session_data["permisos"]
        es_admin = "ALL PRIVILEGES" in permisos

        sidebar_items.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE_ROUNDED, size=40, color=ft.Colors.BLUE_700),
                    ft.Column([
                        ft.Text(page.session_data['user'], weight=ft.FontWeight.BOLD, size=16),
                        ft.Text("Admin" if es_admin else "Operador", size=12, color=ft.Colors.BLUE_GREY_400)
                    ], spacing=0)
                ]),
                padding=ft.Padding.only(bottom=20)
            )
        )

        sidebar_items.controls.append(sidebar_button("Explorador Datos", ft.Icons.STORAGE_ROUNDED, "db"))

        if es_admin:
            sidebar_items.controls.extend([
                sidebar_button("Editor SQL", ft.Icons.TERMINAL_ROUNDED, "query"),
                sidebar_button("Importar CSV", ft.Icons.FILE_OPEN_ROUNDED, "csv"),
                sidebar_button("Backups", ft.Icons.BACKUP_ROUNDED, "backup"),
                sidebar_button("Usuarios", ft.Icons.PEOPLE_ALT_ROUNDED, "users"),
                sidebar_button("Métricas", ft.Icons.INSERT_CHART_ROUNDED, "metrics"),
            ])

        sidebar_items.controls.append(ft.Divider(height=20))

        sidebar_items.controls.append(
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DARK_MODE_ROUNDED, size=20),
                title=ft.Text("Modo Oscuro", size=12),
                trailing=ft.Switch(
                    value=page.theme_mode == ft.ThemeMode.DARK, 
                    on_change=cambiar_tema
                ),
            )
        )

        sidebar_items.controls.append(
            ft.Container(
                content=ft.TextButton(
                    "Cerrar Sesión", 
                    icon=ft.Icons.LOGOUT, 
                    on_click=lambda _: ir_a_login(),
                    style=ft.ButtonStyle(color=ft.Colors.RED_400)
                ),
                padding=ft.Padding.only(top=10)
            )
        )

        layout = ft.Row([
            ft.Container(sidebar_items, width=230, padding=20),
            content_area
        ], expand=True)
        
        page.add(layout)
        cargar_vista("db")

    def on_login(user, permisos):
        page.session_data["user"] = user
        page.session_data["permisos"] = permisos
        mostrar_menu()

    def ir_a_login():
        page.controls.clear()
        page.add(ft.Container(login_view(page, on_login), expand=True, alignment=ft.Alignment.CENTER))
        page.update()

    ir_a_login()

if __name__ == "__main__":
    ft.run(main)