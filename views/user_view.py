import flet as ft
from services.user_service import (
    obtener_usuarios,
    crear_usuario,
    eliminar_usuario,
    obtener_permisos_por_bd,
    actualizar_permisos_usuario,
)
from services.db_service import obtener_bases

def user_view(page: ft.Page):
    usuarios_cache = []
    
    dynamic_container = ft.Column(expand=True)

    txt_mensaje = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    icono_msg = ft.Icon(ft.Icons.INFO_OUTLINE, size=20)
    msg_container = ft.Container(
        content=ft.Row([icono_msg, txt_mensaje], spacing=10),
        padding=10,
        border_radius=8,
        visible=False,
    )

    def mostrar_alerta(msg, es_error=True):
        txt_mensaje.value = msg
        msg_container.visible = True
        msg_container.bgcolor = ft.Colors.RED_50 if es_error else ft.Colors.GREEN_50
        txt_mensaje.color = ft.Colors.RED_700 if es_error else ft.Colors.GREEN_700
        icono_msg.name = ft.Icons.ERROR_OUTLINE if es_error else ft.Icons.CHECK_CIRCLE_OUTLINE
        icono_msg.color = ft.Colors.RED_700 if es_error else ft.Colors.GREEN_700
        page.update()

    def vista_permisos(user_name):
        dynamic_container.controls.clear()
        
        permisos_actuales = obtener_permisos_por_bd(user_name)
        todas_las_bases = obtener_bases()
        
        lista_permisos_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        def crear_fila_db(db_name):
            nombre_clave = db_name.strip().lower()
            permisos_db = permisos_actuales.get(nombre_clave, [])
            tiene_todo = "ALL PRIVILEGES" in permisos_db

            chk_select = ft.Checkbox(label="SELECT", value=tiene_todo or "SELECT" in permisos_db)
            chk_insert = ft.Checkbox(label="INSERT", value=tiene_todo or "INSERT" in permisos_db)
            chk_update = ft.Checkbox(label="UPDATE", value=tiene_todo or "UPDATE" in permisos_db)

            def guardar_permiso_especifico(e):
                nuevos_permisos = []
                if chk_select.value: nuevos_permisos.append("SELECT")
                if chk_insert.value: nuevos_permisos.append("INSERT")
                if chk_update.value: nuevos_permisos.append("UPDATE")
                
                if actualizar_permisos_usuario(user_name, db_name, nuevos_permisos):
                    mostrar_alerta(f"Permisos de '{db_name}' actualizados", False)
                else:
                    mostrar_alerta(f"Error en '{db_name}'")

            return ft.Container(
                content=ft.Row([
                    ft.Text(db_name, weight="bold", width=150),
                    chk_select,
                    chk_insert,
                    chk_update,
                    ft.ElevatedButton(
                        "Actualizar", 
                        icon=ft.Icons.SAVE, 
                        on_click=guardar_permiso_especifico,
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=10,
                border=ft.border.all(1, ft.Colors.BLACK12),
                border_radius=8,
                data=db_name.lower()
            )

        for db in todas_las_bases:
            lista_permisos_column.controls.append(crear_fila_db(db))

        def filtrar_bases(e):
            termino = e.control.value.lower()
            for fila in lista_permisos_column.controls:
                fila.visible = termino in fila.data
            page.update()

        dynamic_container.controls.append(
            ft.Column([
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: volver_a_lista()),
                    ft.Column([
                        ft.Text(f"Permisos de Usuario: {user_name}", size=20, weight="bold"),
                        ft.Text("Gestiona accesos por cada base de datos", size=12, color=ft.Colors.BLUE_GREY_400),
                    ], spacing=0)
                ]),
                ft.Divider(),
                ft.TextField(
                    hint_text="Buscar base de datos...",
                    prefix_icon=ft.Icons.SEARCH_ROUNDED,
                    border_radius=10,
                    on_change=filtrar_bases,
                    height=45,
                    content_padding=10
                ),
                msg_container, 
                ft.Divider(),
                lista_permisos_column
            ], expand=True)
        )
        
        msg_container.visible = False
        page.update()

    def volver_a_lista():
        render_usuarios()
        page.update()

    def render_usuarios(lista=None):
        dynamic_container.controls.clear()
        datos = lista if lista else usuarios_cache
        
        cards = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        for usuario, host in datos:
            cards.controls.append(
                ft.Container(
                    padding=15, border_radius=12, bgcolor=ft.Colors.WHITE,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK12),
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_700),
                            ft.Column([
                                ft.Text(usuario, weight="bold"),
                                ft.Text(host, size=12),
                            ])
                        ], spacing=10),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.SECURITY_ROUNDED,
                                tooltip="Gestionar Permisos",
                                icon_color=ft.Colors.AMBER_800,
                                on_click=lambda e, u=usuario: vista_permisos(u),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.RED_700,
                                on_click=lambda e, u=usuario: eliminar_y_recargar(u),
                            ),
                        ])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            )
        
        header = ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Gestión de Usuarios", size=28, weight="bold"),
                    ft.Text("Administración de accesos", color=ft.Colors.BLUE_GREY_400),
                ]),
                ft.ElevatedButton("Nuevo Usuario", icon=ft.Icons.PERSON_ADD, on_click=modal_nuevo_usuario),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.TextField(hint_text="Buscar usuario...", prefix_icon=ft.Icons.SEARCH, border_radius=15, on_change=filtrar_usuarios),
            msg_container,
            ft.Divider(),
        ])
        
        dynamic_container.controls.extend([header, cards])
        page.update()

    def cargar_lista():
        nonlocal usuarios_cache
        usuarios_cache = obtener_usuarios()
        render_usuarios()

    def eliminar_y_recargar(nombre):
        eliminar_usuario(nombre)
        cargar_lista()
        mostrar_alerta(f"Usuario {nombre} eliminado", False)

    def filtrar_usuarios(e):
        termino = e.control.value.lower()
        filtrados = [u for u in usuarios_cache if termino in u[0].lower()]
        render_usuarios(filtrados)

    def modal_nuevo_usuario(e):
        input_user = ft.TextField(label="Usuario", width=300, border_radius=10)
        input_pass = ft.TextField(
            label="Contraseña", 
            password=True, 
            can_reveal_password=True, 
            width=300,
            border_radius=10
        )

        def cerrar_dialogo(e):
            dialogo.open = False
            page.update()

        def guardar(e):
            if not input_user.value or not input_pass.value:
                mostrar_alerta("Completa todos los campos")
                return
            
            if crear_usuario(input_user.value, input_pass.value):
                dialogo.open = False
                cargar_lista()
                mostrar_alerta("Usuario creado correctamente", False)
            else:
                mostrar_alerta("Error al crear el usuario")
            page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text("Crear Nuevo Usuario"),
            content=ft.Column(
                [
                    ft.Text("Ingresa las credenciales para el nuevo acceso local."),
                    input_user, 
                    input_pass
                ], 
                tight=True,
                spacing=15
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Crear Usuario", bgcolor=ft.Colors.BLUE_700, color="white", on_click=guardar)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

        def guardar(e):
            if crear_usuario(input_user.value, input_pass.value):
                page.dialog.open = False
                cargar_lista()
                mostrar_alerta("Usuario creado", False)
            else:
                mostrar_alerta("Error al crear")

        page.dialog = ft.AlertDialog(
            title=ft.Text("Nuevo Usuario"),
            content=ft.Column([input_user, input_pass], tight=True),
            actions=[ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, 'open', False)),
                     ft.ElevatedButton("Crear", on_click=guardar)]
        )
        page.dialog.open = True
        page.update()

    cargar_lista()
    return ft.Container(content=dynamic_container, padding=20, expand=True)