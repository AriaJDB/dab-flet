import flet as ft
from services.auth_service import login, obtener_privilegios


def login_view(page: ft.Page, on_login):

    user = ft.TextField(label="Usuario")
    password = ft.TextField(label="Contraseña", password=True)

    def iniciar(e):
        u = user.value
        p = password.value

        if not u or not p:
            mostrar("Faltan datos")
            return

        ok = login(u, p)

        if not ok:
            mostrar("Credenciales incorrectas ❌")
            return

        # 🔥 obtener permisos usando root
        permisos = obtener_privilegios("root", "latte", u)

        mostrar("Login correcto ✅")

        on_login(u, permisos)

    def mostrar(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    return ft.Column(
        [
            ft.Text("🔐 Iniciar sesión", size=24, weight="bold"),
            user,
            password,
            ft.ElevatedButton("Entrar", on_click=iniciar)
        ],
        alignment="center",
        horizontal_alignment="center"
    )