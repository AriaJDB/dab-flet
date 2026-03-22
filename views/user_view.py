import flet as ft
from services.user_service import (
    obtener_usuarios, crear_usuario, otorgar_permisos, 
    eliminar_usuario, aplicar_cambios
)
from services.db_service import obtener_bases

def user_view(page: ft.Page):
    txt_mensaje = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    msg_container = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.INFO_OUTLINE, size=20), txt_mensaje], spacing=10),
        padding=10, border_radius=8, visible=False, margin=ft.margin.only(bottom=10)
    )

    main_content = ft.Column(expand=True, spacing=20, scroll=ft.ScrollMode.ADAPTIVE)

    def mostrar_alerta(msg, es_error=True):
        txt_mensaje.value = msg
        msg_container.visible = True
        msg_container.bgcolor = ft.Colors.RED_50 if es_error else ft.Colors.BLUE_50
        txt_mensaje.color = ft.Colors.RED_700 if es_error else ft.Colors.BLUE_700
        msg_container.content.controls[0].color = ft.Colors.RED_700 if es_error else ft.Colors.BLUE_700
        page.update()

    def modal_nuevo_usuario(e):
        input_user = ft.TextField(label="Nombre de Usuario", border_radius=10, prefix_icon=ft.Icons.PERSON)
        input_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, border_radius=10, prefix_icon=ft.Icons.LOCK)
        
        def guardar(e):
            if not input_user.value or not input_pass.value:
                mostrar_alerta("Completa todos los campos")
                return
            
            if crear_usuario(input_user.value, input_pass.value):
                aplicar_cambios()
                page.dialog.open = False
                mostrar_alerta(f"Usuario {input_user.value} creado exitosamente ✅", False)
                render_tabla_usuarios()
            else:
                mostrar_alerta("Error al crear usuario. Verifica si ya existe.")

        page.dialog = ft.AlertDialog(
            title=ft.Text("Registrar Nuevo Usuario"),
            content=ft.Column([input_user, input_pass], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: [setattr(page.dialog, "open", False), page.update()]),
                ft.ElevatedButton("Registrar", on_click=guardar, bgcolor=ft.Colors.BLUE_700, color="white")
            ]
        )
        page.overlay.append(page.dialog)
        page.dialog.open = True
        page.update()

    def modal_editar_permisos(user_name):
        bases = obtener_bases()
        # Añadimos la opción de "*" para permisos globales
        opciones_db = [ft.dropdown.Option("* (Global)")] + [ft.dropdown.Option(db) for db in bases]
        
        dd_db = ft.Dropdown(
            label="Base de Datos / Ámbito", 
            options=opciones_db,
            border_radius=10,
            value="* (Global)"
        )
        
        dd_perm = ft.Dropdown(
            label="Privilegio a Asignar", 
            options=[
                ft.dropdown.Option("ALL PRIVILEGES"),
                ft.dropdown.Option("CREATE"),
                ft.dropdown.Option("DELETE"),
                ft.dropdown.Option("DROP"),
                ft.dropdown.Option("EXECUTE"),
                ft.dropdown.Option("GRANT OPTION"),
                ft.dropdown.Option("INSERT"),
                ft.dropdown.Option("SELECT"),
                ft.dropdown.Option("SHOW DATABASES"),
                ft.dropdown.Option("UPDATE"),
            ], 
            value="SELECT",
            border_radius=10
        )

        def asignar(e):
            # Si el usuario elige "ALL PRIVILEGES", ignoramos la DB seleccionada 
            # y mandamos "*" para que el service use *.*
            db_seleccionada = "*" if dd_perm.value == "ALL PRIVILEGES" or dd_db.value == "* (Global)" else dd_db.value
            
            if otorgar_permisos(user_name, db_seleccionada, dd_perm.value):
                aplicar_cambios()
                page.dialog.open = False
                mostrar_alerta(f"Privilegio {dd_perm.value} aplicado ✅", False)
                page.update()
            else:
                # El mensaje de error ahora será más específico
                mostrar_alerta("Error de nivel de privilegio. Revisa la consola.")

        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Editar Privilegios: {user_name}"),
            content=ft.Column([
                ft.Text("Nota: Esto reemplazará los permisos anteriores en el ámbito seleccionado."),
                dd_db, 
                dd_perm
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: [setattr(page.dialog, "open", False), page.update()]),
                ft.ElevatedButton("Actualizar", on_click=asignar, bgcolor=ft.Colors.AMBER_700, color="white")
            ]
        )
        page.overlay.append(page.dialog)
        page.dialog.open = True
        page.update()

    def render_tabla_usuarios():
        main_content.controls.clear()
        try:
            usuarios = obtener_usuarios()
            
            dt = ft.DataTable(
                heading_row_color=ft.Colors.BLACK12,
                columns=[
                    ft.DataColumn(ft.Text("Usuario", weight="bold")),
                    ft.DataColumn(ft.Text("Host", weight="bold")),
                    ft.DataColumn(ft.Text("Acciones", weight="bold")),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(u[0])),
                        ft.DataCell(ft.Text(u[1])),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.SECURITY_ROUNDED, 
                                icon_color=ft.Colors.AMBER_800, 
                                tooltip="Editar Permisos",
                                on_click=lambda e, n=u[0]: modal_editar_permisos(n)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED, 
                                icon_color="red", 
                                tooltip="Eliminar Usuario",
                                on_click=lambda e, n=u[0]: [eliminar_usuario(n), render_tabla_usuarios(), mostrar_alerta(f"Usuario {n} eliminado")]
                            )
                        ]))
                    ]) for u in usuarios
                ],
                expand=True
            )
            
            main_content.controls.append(ft.Row([dt], scroll=ft.ScrollMode.ALWAYS))
            
        except Exception as e:
            mostrar_alerta(f"Error al cargar la lista: {e}")
        page.update()


    render_tabla_usuarios()

    return ft.Column([
        # Cabecera
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Control de Usuarios", size=28, weight="bold"),
                        ft.Text("Administración de privilegios y accesos", color=ft.Colors.BLUE_GREY_400),
                    ]),
                    ft.ElevatedButton(
                        "Nuevo Usuario", 
                        icon=ft.Icons.PERSON_ADD, 
                        on_click=modal_nuevo_usuario,
                        bgcolor=ft.Colors.BLUE_700,
                        color="white"
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                msg_container,
                ft.Divider(height=1),
            ]),
            padding=10
        ),

        ft.Container(content=main_content, expand=True, padding=10)
    ], expand=True)