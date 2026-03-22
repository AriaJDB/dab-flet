import flet as ft
from services.auth_service import login, obtener_privilegios


def login_view(page: ft.Page, on_login):

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

    user = ft.TextField(
        label="Usuario",
        width=280,
        border_radius=10,
        prefix_icon=ft.Icons.PERSON
    )

    password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        width=280,
        border_radius=10,
        prefix_icon=ft.Icons.LOCK
    )

    def iniciar(e):
        u = user.value
        p = password.value

        if not u or not p:
            mostrar_alerta("Faltan datos")
            return

        ok = login(u, p)

        if not ok:
            mostrar_alerta("Credenciales incorrectas")
            return

        permisos = obtener_privilegios("root", "latte", u)

        mostrar_alerta("Login correcto", False)

        on_login(u, permisos)

    return ft.Container(
    expand=True,
    alignment=ft.Alignment.CENTER,
    content=ft.Container(
        width=500,
        height=400,
        padding=30,
        border_radius=15,
        bgcolor=ft.Colors.WHITE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.SURFACE_CONTAINER_HIGHEST,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK26),

        content=ft.Column(
            [
                ft.Text("🔐 Iniciar sesión", size=28, weight="bold"),
                ft.Text("Accede a LatteDB Manager", color=ft.Colors.BLUE_GREY_400),

                msg_container,

                user,
                password,

                ft.ElevatedButton(
                    "Entrar",
                    on_click=iniciar,
                    width=200,
                    bgcolor=ft.Colors.BLUE_700,
                    color="white"
                )
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        )
    )
)