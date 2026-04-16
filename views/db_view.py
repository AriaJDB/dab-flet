import flet as ft
from .db_components.render_bases import get_bases_ui
from .db_components.render_tablas import get_tablas_ui
from .db_components.render_datos import get_datos_ui

def db_view(page: ft.Page, session_data):
    permisos_data = session_data.get("permisos", {})
    es_admin = permisos_data.get("es_admin", False)
    permisos_bases = permisos_data.get("permisos_bd", {})
    

    estado = {
        "nivel": "bases",
        "db_seleccionada": None,
        "tabla_seleccionada": None
    }
    cache_manager = {"datos": []}

    def tiene_acceso_db(nombre_db):
        if es_admin:
            return True
        return nombre_db in permisos_bases

    def tiene_permiso(db, permiso):
        if es_admin:
            return True
        return permiso.upper() in permisos_bases.get(db, [])

    def get_list_container_style():
        return {
            "bgcolor": ft.Colors.SURFACE_CONTAINER_HIGHEST
            if page.theme_mode == ft.ThemeMode.DARK
            else ft.Colors.WHITE,
            "border_radius": 10,
            "border": ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        }

    breadcrumb_row = ft.Row(
        spacing=5,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    main_content = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.ADAPTIVE
    )

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
            msg_container.bgcolor = (
                ft.Colors.RED_900
                if page.theme_mode == ft.ThemeMode.DARK
                else ft.Colors.RED_50
            )
            txt_mensaje.color = (
                ft.Colors.WHITE
                if page.theme_mode == ft.ThemeMode.DARK
                else ft.Colors.RED_700
            )
            icono_msg.name = ft.Icons.ERROR_OUTLINE
            icono_msg.color = txt_mensaje.color
        else:
            msg_container.bgcolor = (
                ft.Colors.BLUE_900
                if page.theme_mode == ft.ThemeMode.DARK
                else ft.Colors.BLUE_50
            )
            txt_mensaje.color = (
                ft.Colors.WHITE
                if page.theme_mode == ft.ThemeMode.DARK
                else ft.Colors.BLUE_700
            )
            icono_msg.name = ft.Icons.CHECK_CIRCLE_OUTLINE
            icono_msg.color = txt_mensaje.color

        page.update()

    def filtrar_contenido(e):
        termino = e.control.value.lower()
        main_content.controls.clear()

        if estado["nivel"] == "bases":
            filtrados = [d for d in cache_manager["datos"] if termino in d.lower()]
            main_content.controls.extend(
                get_bases_ui(es_admin, tiene_acceso_db, ir_a_nivel, mostrar_alerta, 
                             get_list_container_style, cache_manager, session_data, filtrados)
            )

        elif estado["nivel"] == "tablas":
            filtrados = [t for t in cache_manager["datos"] if termino in t.lower()]
            main_content.controls.extend(
                get_tablas_ui(estado["db_seleccionada"], es_admin, permisos_bases,
                              lambda p: tiene_permiso(estado["db_seleccionada"], p),
                              ir_a_nivel, get_list_container_style, cache_manager, page, filtrados)
            )

        elif estado["nivel"] == "datos":
            filtrados = [row for row in cache_manager["datos"] if any(termino in str(c).lower() for c in row)]
            main_content.controls.extend(
                get_datos_ui(estado["db_seleccionada"], estado["tabla_seleccionada"], es_admin,
                             permisos_bases.get(estado["db_seleccionada"], []),
                             ir_a_nivel, get_list_container_style, cache_manager, page, filtrados)
            )
        page.update()

    search_field = ft.TextField(
        hint_text="Buscar...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=filtrar_contenido,
        height=40,
        width=250,
        border_radius=10,
        text_size=14,
        bgcolor=(
            ft.Colors.SURFACE_VARIANT
            if page.theme_mode == ft.ThemeMode.DARK
            else ft.Colors.GREY_50
        ),
    )

    def ir_a_nivel(nivel, nombre=None):
        search_field.value = ""
        msg_container.visible = False
        estado["nivel"] = nivel
        main_content.controls.clear()

        if nivel == "bases":
            estado["db_seleccionada"] = None
            estado["tabla_seleccionada"] = None
            main_content.controls.extend(
                get_bases_ui(
                    es_admin,
                    tiene_acceso_db,
                    ir_a_nivel,
                    mostrar_alerta,
                    get_list_container_style,
                    cache_manager,
                    session_data,
                    None
                )
            )

        # --- Dentro de ir_a_nivel en db_view.py ---

        elif nivel == "tablas":
            if nombre:
                estado["db_seleccionada"] = nombre
            main_content.controls.extend(
                get_tablas_ui(
                    estado["db_seleccionada"],
                    es_admin,
                    permisos_bases,
                    lambda permiso: tiene_permiso(estado["db_seleccionada"], permiso), 
                    ir_a_nivel,
                    get_list_container_style,
                    cache_manager,
                    page
                )
            )

        elif nivel == "datos":
            if nombre:
                estado["tabla_seleccionada"] = nombre
            main_content.controls.extend(
                get_datos_ui(
                    estado["db_seleccionada"],
                    estado["tabla_seleccionada"],
                    es_admin,
                    permisos_bases.get(estado["db_seleccionada"], []), 
                    ir_a_nivel,
                    get_list_container_style,
                    cache_manager,
                    page
                )
            )

        actualizar_breadcrumbs()
        page.update()

    def actualizar_breadcrumbs():
        breadcrumb_row.controls.clear()
        breadcrumb_row.controls.append(
            ft.TextButton(
                "Inicio",
                icon=ft.Icons.HOME,
                on_click=lambda _: ir_a_nivel("bases")
            )
        )

        if estado["db_seleccionada"]:
            breadcrumb_row.controls.extend([
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16),
                ft.TextButton(
                    estado["db_seleccionada"],
                    on_click=lambda _: ir_a_nivel("tablas")
                )
            ])

        if estado["tabla_seleccionada"]:
            breadcrumb_row.controls.extend([
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16),
                ft.Text(
                    estado["tabla_seleccionada"],
                    weight=ft.FontWeight.BOLD,
                    size=14,
                    color=ft.Colors.BLUE
                )
            ])

    ir_a_nivel("bases")

    return ft.Column(
        [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column([
                            ft.Text(
                                "Explorador de Datos",
                                size=22,
                                weight=ft.FontWeight.BOLD
                            ),
                            breadcrumb_row
                        ]),
                        search_field
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=20
            ),
            msg_container,
            ft.Container(
                content=main_content,
                expand=True,
                padding=ft.padding.only(
                    left=20,
                    right=20,
                    bottom=20
                )
            )
        ],
        expand=True
    )