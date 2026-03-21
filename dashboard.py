import flet as ft
from views.db_view import db_view
from views.table_view import table_view
from views.backup_view import backup_view
from views.csv_view import csv_view

def main(page: ft.Page):
    page.title = "Administrador DB"
    page.window_width = 1100
    page.window_height = 650

    content = ft.Column(expand=True)

    def cambiar_vista(e):
        content.controls.clear()

        if e.control.data == "db":
            content.controls.append(db_view(page))

        elif e.control.data == "tables":
            content.controls.append(table_view(page))

        elif e.control.data == "backup":
            content.controls.append(backup_view(page))
        
        elif e.control.data == "csv":
            content.controls.append(csv_view(page))

        else:
            content.controls.append(ft.Text("Sección en construcción 🏗️"))

        page.update()

    sidebar = ft.Column(
        [
            ft.Text("⚙️ Panel", size=22, weight="bold"),
            ft.Divider(),

            ft.TextButton("Bases de datos", on_click=cambiar_vista, data="db"),
            ft.TextButton("Tablas", on_click=cambiar_vista, data="tables"),
            ft.TextButton("Backups", on_click=cambiar_vista, data="backup"),
            ft.TextButton("CSV", on_click=cambiar_vista, data="csv"),
            ft.TextButton("Usuarios", on_click=cambiar_vista, data="users"),
            ft.TextButton("Rendimiento", on_click=cambiar_vista, data="stats"),
        ],
        width=200
    )

    layout = ft.Row(
        [
            sidebar,
            ft.VerticalDivider(),
            ft.Container(content, expand=True, padding=20)
        ],
        expand=True
    )

    page.add(layout)

ft.app(target=main)