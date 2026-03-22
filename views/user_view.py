import flet as ft
from services.user_service import (
    obtener_usuarios, crear_usuario, otorgar_permisos, 
    eliminar_usuario, aplicar_cambios
)
from services.db_service import obtener_bases

def user_view(page: ft.Page):
    usuarios_cache = []

    txt_mensaje = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    icono_msg = ft.Icon(ft.Icons.INFO_OUTLINE, size=20)

    msg_container = ft.Container(
        content=ft.Row([icono_msg, txt_mensaje], spacing=10),
        padding=10,
        border_radius=8,
        visible=False,
        margin=ft.margin.only(bottom=10)
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

    def filtrar_usuarios(e):
        termino = e.control.value.lower()
        filtrados = [u for u in usuarios_cache if termino in u[0].lower()]
        render_usuarios(filtrados)

    def modal_nuevo_usuario(e):
        input_user = ft.TextField(
            label="Usuario",
            width=300,
            border_radius=10,
            prefix_icon=ft.Icons.PERSON
        )

        input_pass = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            border_radius=10,
            prefix_icon=ft.Icons.LOCK
        )

        def guardar(e):
            if not input_user.value or not input_pass.value:
                mostrar_alerta("Completa todos los campos")
                return

            if crear_usuario(input_user.value, input_pass.value):
                aplicar_cambios()
                cerrar_dialog()
                mostrar_alerta(f"Usuario {input_user.value} creado", False)
                cargar_lista()
            else:
                mostrar_alerta("Error al crear usuario")

        content = ft.Container(
            width=350,
            height=150,
            content=ft.Column(
                [
                    input_user,
                    input_pass
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER  # 🔥 CLAVE
            )
        )

        page.dialog = ft.AlertDialog(
            title=ft.Text("Nuevo Usuario"),
            content=content,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialog()),
                ft.ElevatedButton("Crear", on_click=guardar)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.overlay.append(page.dialog)
        page.dialog.open = True
        page.update()

    def cerrar_dialog():
        page.dialog.open = False
        page.update()

    def modal_editar_permisos(user_name):
        from services.user_service import obtener_permisos_usuario
        permisos_actuales = obtener_permisos_usuario(user_name)

        bases = obtener_bases()
        privilegios = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP"]

        checks = {
            p: ft.Checkbox(label=p, value=p in permisos_actuales)
            for p in privilegios
        }

        dd_db = ft.Dropdown(
            label="Base",
            width=280,
            options=[ft.dropdown.Option("*")] + [ft.dropdown.Option(db) for db in bases],
            value="*",
            border_radius=10
        )

        lista_checks = ft.Column(
            list(checks.values()),
            height=180,
            scroll=ft.ScrollMode.AUTO
        )

        def guardar(e):
            for p, check in checks.items():
                if check.value:
                    otorgar_permisos(user_name, dd_db.value, p)

            aplicar_cambios()
            cerrar_dialog()
            mostrar_alerta("Permisos actualizados", False)

        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Permisos: {user_name}"),
            content=ft.Container(
                width=320,
                height=300,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        dd_db,
                        ft.Divider(),
                        lista_checks
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: cerrar_dialog()),
                ft.ElevatedButton("Guardar", on_click=guardar)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.overlay.append(page.dialog)
        page.dialog.open = True
        page.update()

    def render_usuarios(lista=None):
        main_content.controls.clear()
        datos = lista if lista else usuarios_cache

        is_dark = page.theme_mode == ft.ThemeMode.DARK

        card_bg = ft.Colors.SURFACE_CONTAINER_HIGHEST if is_dark else ft.Colors.WHITE
        text_secondary = ft.Colors.GREY_400 if is_dark else ft.Colors.GREY_600
        border_color = ft.Colors.GREY_700 if is_dark else ft.Colors.GREY_300

        for u in datos:
            usuario, host = u[0], u[1]

            card = ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_700),
                        ft.Column([
                            ft.Text(usuario, weight="bold"),
                            ft.Text(host, size=12, color=text_secondary)
                        ])
                    ], spacing=10),

                    ft.Row([
                        ft.IconButton(
                            ft.Icons.SECURITY_ROUNDED,
                            tooltip="Permisos",
                            icon_color=ft.Colors.AMBER_800,
                            on_click=lambda e, n=usuario: modal_editar_permisos(n)
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE_ROUNDED,
                            tooltip="Eliminar",
                            icon_color=ft.Colors.RED_700,
                            on_click=lambda e, n=usuario: eliminar(n)
                        )
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                padding=15,
                border_radius=12,
                bgcolor=card_bg,
                border=ft.border.all(1, border_color),
                shadow=ft.BoxShadow(
                    blur_radius=6,
                    color=ft.Colors.BLACK26 if is_dark else ft.Colors.BLACK12
                )
            )

            main_content.controls.append(card)

    page.update()

    def eliminar(nombre):
        eliminar_usuario(nombre)
        cargar_lista()
        mostrar_alerta(f"Usuario {nombre} eliminado", False)

    # --- CARGA ---
    def cargar_lista():
        nonlocal usuarios_cache
        usuarios_cache = obtener_usuarios()
        render_usuarios()

    main_content = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)

    cargar_lista()

    # --- UI ---
    return ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Gestión de Usuarios", size=28, weight="bold"),
                        ft.Text("Administración de accesos", color=ft.Colors.BLUE_GREY_400),
                    ]),
                    ft.ElevatedButton("Nuevo Usuario", icon=ft.Icons.PERSON_ADD, on_click=modal_nuevo_usuario)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.TextField(
                    hint_text="Buscar usuario...",
                    prefix_icon=ft.Icons.SEARCH,
                    border_radius=15,
                    on_change=filtrar_usuarios
                ),

                msg_container,
                ft.Divider()
            ]),
            padding=10
        ),

        ft.Container(
            content=main_content,
            expand=True,
            padding=10,
            bgcolor=ft.Colors.SURFACE if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_50
        )
    ], expand=True)