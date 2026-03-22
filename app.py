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
    

    page.title = "Administrador de Base de Datos"
    page.window_width = 1000
    page.window_height = 600

    # 🧠 estado global simple
    usuario_actual = {"user": None, "permisos": ""}

    # 🧱 layout
    menu = ft.Column(width=200)
    content = ft.Column(expand=True)

    layout = ft.Row(
        [
            ft.Container(menu, bgcolor="#eeeeee", padding=10),
            ft.VerticalDivider(width=1),
            ft.Container(content, expand=True, padding=10)
        ],
        expand=True
    )

    page.add(layout)

    # 🔄 cambiar vista
    def cargar_vista(nombre):

        content.controls.clear()

        if nombre == "db":
            content.controls.append(db_view(page))

        elif nombre == "tables":
            content.controls.append(table_view(page))

        elif nombre == "csv":
            content.controls.append(csv_view(page))

        elif nombre == "backup":
            content.controls.append(backup_view(page))

        elif nombre == "users":
            content.controls.append(user_view(page))

        elif nombre == "metrics":
            content.controls.append(metrics_view(page))

        page.update()

    # 🧠 construir menú según permisos
    def mostrar_menu():

        menu.controls.clear()
        content.controls.clear()

        permisos = usuario_actual["permisos"]

        menu.controls.append(
            ft.Text(f"👤 {usuario_actual['user']}", weight="bold")
        )

        menu.controls.append(ft.Divider())

        # 🔥 ADMIN TOTAL
        if "ALL PRIVILEGES" in permisos:

            menu.controls.append(
                ft.TextButton("📦 Bases de datos", on_click=lambda e: cargar_vista("db"))
            )

            menu.controls.append(
                ft.TextButton("📊 Tablas", on_click=lambda e: cargar_vista("tables"))
            )

            menu.controls.append(
                ft.TextButton("📄 CSV", on_click=lambda e: cargar_vista("csv"))
            )

            menu.controls.append(
                ft.TextButton("💾 Backups", on_click=lambda e: cargar_vista("backup"))
            )

            menu.controls.append(
                ft.TextButton("🔐 Usuarios", on_click=lambda e: cargar_vista("users"))
            )

            menu.controls.append(
                ft.TextButton("📊 Métricas", on_click=lambda e: cargar_vista("metrics"))
            )

        else:
            # 👁️ permisos limitados
            if "SELECT" in permisos:
                menu.controls.append(
                    ft.TextButton("📊 Ver tablas", on_click=lambda e: cargar_vista("tables"))
                )

            if "INSERT" in permisos:
                menu.controls.append(
                    ft.TextButton("➕ Insertar datos", on_click=lambda e: cargar_vista("tables"))
                )

        page.update()

    # 🔐 cuando hace login
    def on_login(user, permisos):
        usuario_actual["user"] = user
        usuario_actual["permisos"] = permisos

        mostrar_menu()

    # 🚪 cerrar sesión (extra)
    def logout(e):
        usuario_actual["user"] = None
        usuario_actual["permisos"] = ""

        menu.controls.clear()
        content.controls.clear()

        content.controls.append(login_view(page, on_login))
        page.update()

    # 🚀 iniciar app con login
    content.controls.append(login_view(page, on_login))
    page.update()


# ▶️ ejecutar app
ft.run(main)