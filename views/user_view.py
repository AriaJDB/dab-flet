import flet as ft
from services.user_service import *
from services.db_service import obtener_bases

def user_view(page: ft.Page):

    lista = ft.Column()

    input_user = ft.TextField(label="Usuario")
    input_pass = ft.TextField(label="Contraseña", password=True)

    dropdown_db = ft.Dropdown(label="Base de datos")
    dropdown_perm = ft.Dropdown(
        label="Permisos",
        options=[
            ft.dropdown.Option("ALL PRIVILEGES"),
            ft.dropdown.Option("SELECT"),
            ft.dropdown.Option("INSERT"),
            ft.dropdown.Option("UPDATE"),
            ft.dropdown.Option("DELETE")
        ]
    )

    # 🔄 cargar datos
    def cargar():
        lista.controls.clear()

        usuarios = obtener_usuarios()
        bases = obtener_bases()

        dropdown_db.options = [ft.dropdown.Option(db) for db in bases]

        for u in usuarios:
            lista.controls.append(ft.Text(f"{u[0]}@{u[1]}"))

        page.update()

    # 👤 crear usuario
    def crear(e):
        user = input_user.value
        password = input_pass.value

        if not user or not password:
            mostrar("Faltan datos")
            return

        ok = crear_usuario(user, password)

        if ok:
            aplicar_cambios()
            mostrar("Usuario creado ✅")
            cargar()
        else:
            mostrar("Error al crear usuario ❌")

    # 🔐 asignar permisos
    def asignar(e):
        user = input_user.value
        db = dropdown_db.value
        perm = dropdown_perm.value

        if not user or not db or not perm:
            mostrar("Faltan datos")
            return

        ok = otorgar_permisos(user, db, perm)

        if ok:
            aplicar_cambios()
            mostrar("Permisos asignados ✅")
        else:
            mostrar("Error al asignar permisos ❌")

    # 🔔 mensaje
    def mostrar(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    cargar()

    return ft.Column(
        [
            ft.Text("🔐 Usuarios MariaDB", size=24, weight="bold"),

            ft.Text("Crear usuario:", weight="bold"),
            input_user,
            input_pass,
            ft.ElevatedButton("Crear usuario", on_click=crear),

            ft.Divider(),

            ft.Text("Asignar permisos:", weight="bold"),
            dropdown_db,
            dropdown_perm,
            ft.ElevatedButton("Asignar permisos", on_click=asignar),

            ft.Divider(),

            ft.Text("Usuarios existentes:", weight="bold"),
            lista
        ]
    )