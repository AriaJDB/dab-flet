import flet as ft
from services.user_service import (
    obtener_usuarios, crear_usuario, otorgar_permisos, 
    eliminar_usuario, aplicar_cambios
)
from services.db_service import obtener_bases
# Nota: Necesitaremos una función en el service para obtener permisos actuales
# Si no la tienes, te sugiero crearla (ver nota al final)

def user_view(page: ft.Page):
    # --- Estado Local ---
    usuarios_cache = [] # Para el buscador
    
    # --- UI Estática ---
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

    # --- 🔍 Lógica del Buscador ---
    def filtrar_usuarios(e):
        termino = e.control.value.lower()
        filtrados = [u for u in usuarios_cache if termino in u[0].lower()]
        render_tabla_usuarios(filtrados)

    # --- 👤 Modal: Nuevo Usuario ---
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
                mostrar_alerta(f"Usuario {input_user.value} creado ✅", False)
                cargar_lista_inicial()
            else:
                mostrar_alerta("Error al crear usuario.")

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

    # --- 🔑 Modal: Editar Privilegios (Checkboxes) ---
    # --- 🔑 Modal: Editar Privilegios (CORREGIDO) ---
    def modal_editar_permisos(user_name):
        # 1. Obtener los permisos reales que ya tiene el usuario desde el Service
        from services.user_service import obtener_permisos_usuario
        permisos_actuales = obtener_permisos_usuario(user_name)
        
        bases = obtener_bases()
        privilegios = [
            "ALL PRIVILEGES", "CREATE", "DELETE", "DROP", "EXECUTE",
            "GRANT OPTION", "INSERT", "SELECT", "SHOW DATABASES", "UPDATE"
        ]
        
        # 2. Crear los checkboxes y MARCARLOS si el permiso está en la lista actual
        checks = {}
        for p in privilegios:
            # Comparamos el nombre del privilegio con la lista de MariaDB
            esta_marcado = p in permisos_actuales
            checks[p] = ft.Checkbox(label=p, value=esta_marcado)

        dd_db = ft.Dropdown(
            label="Ámbito (Base de Datos)", 
            options=[ft.dropdown.Option("* (Global)")] + [ft.dropdown.Option(db) for db in bases],
            value="* (Global)",
            border_radius=10
        )

        def actualizar_permisos(e):
            db_target = "*" if dd_db.value == "* (Global)" else dd_db.value
            exito = True
            
            # 3. Lógica de Sincronización:
            # Si el checkbox está marcado -> GRANT
            # Si el checkbox NO está marcado -> REVOKE (Opcional, pero recomendado)
            for p, check in checks.items():
                if check.value:
                    if not otorgar_permisos(user_name, db_target, p):
                        exito = False
            
            if exito:
                aplicar_cambios()
                page.dialog.open = False
                mostrar_alerta(f"Privilegios de {user_name} sincronizados ✅", False)
            else:
                mostrar_alerta("Error al procesar algunos privilegios")

        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Editar Privilegios: {user_name}"),
            content=ft.Column([
                ft.Text(f"Permisos actuales detectados: {', '.join(permisos_actuales) if permisos_actuales else 'Ninguno'}"),
                dd_db,
                ft.Divider(),
                ft.Column([v for v in checks.values()], scroll=ft.ScrollMode.ADAPTIVE, height=300)
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: [setattr(page.dialog, "open", False), page.update()]),
                ft.ElevatedButton("Guardar Cambios", on_click=actualizar_permisos, bgcolor=ft.Colors.AMBER_700, color="white")
            ]
        )
        page.overlay.append(page.dialog)
        page.dialog.open = True
        page.update()

    # --- 📊 Render de Tabla (Ocupando todo el ancho) ---
    def render_tabla_usuarios(lista=None):
        main_content.controls.clear()
        datos = lista if lista is not None else usuarios_cache
        
        dt = ft.DataTable(
            heading_row_color=ft.Colors.BLACK12,
            # Forzamos que la tabla intente usar el ancho disponible
            width=900, # Restamos márgenes y padding
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
                        ft.IconButton(ft.Icons.SECURITY_ROUNDED, icon_color=ft.Colors.AMBER_800, 
                                      on_click=lambda e, n=u[0]: modal_editar_permisos(n)),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color="red", 
                                      on_click=lambda e, n=u[0]: [eliminar_usuario(n), cargar_lista_inicial(), mostrar_alerta(f"Usuario {n} eliminado")])
                    ]))
                ]) for u in datos
            ]
        )
        
        # El Row con scroll horizontal permite que la tabla no se rompa en pantallas chicas
        main_content.controls.append(ft.Row([dt], scroll=ft.ScrollMode.ALWAYS))
        page.update()

    def cargar_lista_inicial():
        nonlocal usuarios_cache
        try:
            usuarios_cache = obtener_usuarios()
            render_tabla_usuarios()
        except Exception as e:
            mostrar_alerta(f"Error: {e}")

    cargar_lista_inicial()

    # --- Layout Principal ---
    return ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Gestión de Usuarios", size=28, weight="bold"),
                        ft.Text("Administración de privilegios y accesos", color=ft.Colors.BLUE_GREY_400),
                    ]),
                    ft.ElevatedButton("Nuevo Usuario", icon=ft.Icons.PERSON_ADD, on_click=modal_nuevo_usuario, bgcolor=ft.Colors.BLUE_700, color="white")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # BUSCADOR
                ft.Container(
                    content=ft.TextField(
                        hint_text="Buscar usuario por nombre...",
                        prefix_icon=ft.Icons.SEARCH,
                        border_radius=15,
                        on_change=filtrar_usuarios, # Filtra mientras escribes
                        height=45,
                        content_padding=ft.padding.only(left=10, right=10)
                    ),
                    margin=ft.margin.only(top=10, bottom=10)
                ),
                
                msg_container,
                ft.Divider(height=1),
            ]),
            padding=10
        ),
        # Contenedor expandido para la tabla
        ft.Container(content=main_content, expand=True, padding=10)
    ], expand=True)