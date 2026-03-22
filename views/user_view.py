import flet as ft
from services.user_service import *
from services.db_service import obtener_bases

def user_view(page: ft.Page):
    # --- Contenedores Dinámicos ---
    lista_usuarios = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10)

    # --- Inputs Estilizados ---
    input_user = ft.TextField(
        label="Nombre de Usuario",
        hint_text="Ej: analista_datos",
        width=300,
        border_radius=10,
        prefix_icon=ft.Icons.PERSON_ADD_ALT_1_ROUNDED
    )
    
    input_pass = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True, # Útil para verificar lo que escribes
        width=300,
        border_radius=10,
        prefix_icon=ft.Icons.LOCK_OUTLINED
    )

    dropdown_db = ft.Dropdown(
        label="Base de Datos",
        width=300,
        border_radius=10,
    )

    dropdown_perm = ft.Dropdown(
        label="Tipo de Permiso",
        width=300,
        border_radius=10,
        options=[
            ft.dropdown.Option("ALL PRIVILEGES"),
            ft.dropdown.Option("SELECT"),
            ft.dropdown.Option("INSERT"),
            ft.dropdown.Option("UPDATE"),
            ft.dropdown.Option("DELETE")
        ]
    )

    # 🔄 Cargar datos
    def cargar_datos():
        lista_usuarios.controls.clear()
        try:
            usuarios = obtener_usuarios()
            bases = obtener_bases()

            dropdown_db.options = [ft.dropdown.Option(db) for db in bases]

            for u in usuarios:
                # u[0] es user, u[1] es host
                lista_usuarios.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, color=ft.Colors.BLUE_GREY_400),
                            ft.Text(f"{u[0]}", weight=ft.FontWeight.BOLD, expand=True),
                            ft.Text(f"Host: {u[1]}", color=ft.Colors.BLUE_GREY_200, size=12),
                            ft.IconButton(
                                icon=ft.Icons.SHIELD_OUTLINED,
                                icon_color=ft.Colors.BLUE_400,
                                tooltip="Ver permisos",
                                on_click=lambda e, name=u[0]: (input_user.set_value(name), page.update())
                            )
                        ]),
                        padding=ft.Padding.all(12),
                        border_radius=10,
                        bgcolor=ft.Colors.GREY_50,
                    )
                )
        except Exception as e:
            lista_usuarios.controls.append(ft.Text(f"Error: {e}", color="red"))
        
        page.update()

    # 👤 Acciones
    def ejecutar_creacion(e):
        if not input_user.value or not input_pass.value:
            notificar("Completa usuario y contraseña")
            return

        if crear_usuario(input_user.value, input_pass.value):
            aplicar_cambios()
            notificar("Usuario creado exitosamente ✅")
            input_pass.value = ""
            cargar_datos()
        else:
            notificar("Error al crear el usuario ❌")

    def ejecutar_asignacion(e):
        if not all([input_user.value, dropdown_db.value, dropdown_perm.value]):
            notificar("Faltan datos para asignar permisos")
            return

        if otorgar_permisos(input_user.value, dropdown_db.value, dropdown_perm.value):
            aplicar_cambios()
            notificar(f"Permiso {dropdown_perm.value} otorgado ✅")
        else:
            notificar("Error al asignar permisos ❌")

    def notificar(msg):
        page.open(ft.SnackBar(ft.Text(msg)))

    cargar_datos()

    # --- DISEÑO FINAL PROFESIONAL ---
    return ft.Column([
        # Header
        ft.Row([
            ft.Column([
                ft.Text("Control de Acceso", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Gestiona usuarios y privilegios del servidor", color=ft.Colors.BLUE_GREY_400),
            ])
        ]),

        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

        ft.Row([
            # IZQUIERDA: Formulario de Gestión
            ft.Column([
                # Card: Crear Usuario
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.PERSON_ADD_ROUNDED, color=ft.Colors.BLUE_700), ft.Text("Nuevo Usuario", weight="bold")]),
                        input_user,
                        input_pass,
                        ft.Button(
                            "Registrar Usuario",
                            on_click=ejecutar_creacion,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
                        )
                    ], spacing=15),
                    padding=25, bgcolor=ft.Colors.WHITE, border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
                ),

                # Card: Asignar Permisos
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.VPN_KEY_ROUNDED, color=ft.Colors.AMBER_700), ft.Text("Asignar Privilegios", weight="bold")]),
                        dropdown_db,
                        dropdown_perm,
                        ft.Button(
                            "Conceder Permisos",
                            on_click=ejecutar_asignacion,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE)
                        )
                    ], spacing=15),
                    padding=25, bgcolor=ft.Colors.WHITE, border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
                )
            ], width=350, spacing=20),

            # DERECHA: Lista de Usuarios Existentes
            ft.Container(
                content=ft.Column([
                    ft.Text("Cuentas en el Servidor", weight=ft.FontWeight.BOLD, size=18),
                    ft.Divider(),
                    lista_usuarios
                ]),
                expand=True,
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
            )
        ], expand=True, spacing=20)
    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)