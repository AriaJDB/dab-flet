import flet as ft
from services.db_service import obtener_bases, eliminar_base
from services.table_service import obtener_tablas, obtener_columnas, obtener_datos

def db_view(page: ft.Page):
    # --- Estado de la Vista ---
    estado = {
        "nivel": "bases", # bases, tablas, datos
        "db_seleccionada": None,
        "tabla_seleccionada": None
    }

    # Contenedor principal donde renderizaremos el contenido dinámico
    main_content = ft.Column(expand=True, spacing=20)
    breadcrumb_row = ft.Row(spacing=5)

    # --- Componente: Breadcrumbs ---
    def actualizar_breadcrumbs():
        breadcrumb_row.controls.clear()
        
        # Nivel 1: Inicio / Bases
        breadcrumb_row.controls.append(
            ft.TextButton("Bases de Datos", on_click=lambda _: ir_a_nivel("bases"))
        )

        # Nivel 2: Base seleccionada
        if estado["db_seleccionada"]:
            breadcrumb_row.controls.append(ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=ft.Colors.GREY_400))
            breadcrumb_row.controls.append(
                ft.TextButton(estado["db_seleccionada"], on_click=lambda _: ir_a_nivel("tablas"))
            )

        # Nivel 3: Tabla seleccionada
        if estado["tabla_seleccionada"]:
            breadcrumb_row.controls.append(ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=ft.Colors.GREY_400))
            breadcrumb_row.controls.append(
                ft.Text(estado["tabla_seleccionada"], weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
            )
        
        page.update()

    # --- Lógica de Navegación ---
    def ir_a_nivel(nivel, nombre=None):
        estado["nivel"] = nivel
        if nivel == "bases":
            estado["db_seleccionada"] = None
            estado["tabla_seleccionada"] = None
            render_bases()
        elif nivel == "tablas":
            if nombre: estado["db_seleccionada"] = nombre
            estado["tabla_seleccionada"] = None
            render_tablas()
        elif nivel == "datos":
            if nombre: estado["tabla_seleccionada"] = nombre
            render_datos()
        
        actualizar_breadcrumbs()

    # --- Renderizado: Nivel 1 (Bases de Datos) ---
    def render_bases():
        main_content.controls.clear()
        
        # Usamos una columna para que se apilen verticalmente
        lista_bases = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        
        try:
            bases = obtener_bases()
            for db in bases:
                lista_bases.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DATA_ARRAY_ROUNDED, color=ft.Colors.BLUE_700),
                            ft.Text(db, weight=ft.FontWeight.W_500, size=16, expand=True),
                            ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=14, color=ft.Colors.GREY_400)
                        ]),
                        padding=20,
                        # Fondo adaptable al modo oscuro
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
                        border_radius=10,
                        on_click=lambda e, n=db: ir_a_nivel("tablas", n),
                        # Efecto visual al pasar el mouse
                        on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.BLUE_50 if (e.data == "true" and page.theme_mode == ft.ThemeMode.LIGHT) else (ft.Colors.WHITE10 if e.data == "true" else None)) or e.control.update()
                    )
                )
            
            if not bases:
                main_content.controls.append(ft.Text("No se encontraron bases de datos.", italic=True))
            else:
                main_content.controls.append(lista_bases)

        except Exception as ex:
            main_content.controls.append(ft.Text(f"Error al cargar bases: {ex}", color="red"))

        page.update()

    # --- Renderizado: Nivel 2 (Tablas) ---
    def render_tablas():
        main_content.controls.clear()
        lista = ft.Column(spacing=10)
        
        try:
            tablas = obtener_tablas(estado["db_seleccionada"])
            for t in tablas:
                lista.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.TABLE_CHART_ROUNDED, color=ft.Colors.BLUE_400),
                            ft.Text(t, size=16, expand=True),
                            ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=14, color=ft.Colors.GREY_400)
                        ]),
                        padding=20,
                        border_radius=10,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
                        on_click=lambda e, n=t: ir_a_nivel("datos", n)
                    )
                )
        except Exception as ex:
            main_content.controls.append(ft.Text(f"Error: {ex}", color="red"))

        main_content.controls.append(lista)
        page.update()

    # --- Renderizado: Nivel 3 (Datos de la Tabla) ---
    def render_datos():
        main_content.controls.clear()
        
        try:
            # Obtener columnas y filas
            columnas_db = obtener_columnas(estado["db_seleccionada"], estado["tabla_seleccionada"])
            datos = obtener_datos(estado["db_seleccionada"], estado["tabla_seleccionada"])

            # Crear el DataTable de Flet
            dt = ft.DataTable(
                border=ft.border.all(1, ft.Colors.BLACK12),
                border_radius=10,
                heading_row_color=ft.Colors.BLUE_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.WHITE10,
                columns=[ft.DataColumn(ft.Text(col[0], weight="bold")) for col in columnas_db],
                rows=[
                    ft.DataRow(cells=[ft.DataCell(ft.Text(str(valor))) for valor in fila])
                    for fila in datos
                ]
            )

            # Contenedor con scroll horizontal por si la tabla es muy ancha
            main_content.controls.append(
                ft.Container(
                    content=ft.Column([dt], scroll=ft.ScrollMode.ADAPTIVE),
                    padding=10,
                    bgcolor=ft.Colors.WHITE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.BLACK12,
                    border_radius=15
                )
            )
        except Exception as ex:
            main_content.controls.append(ft.Text(f"Error al cargar datos: {ex}", color="red"))
        
        page.update()

    # --- Inicio de la Vista ---
    ir_a_nivel("bases")
    
    return ft.Column([
        ft.Container(breadcrumb_row, padding=ft.Padding.only(bottom=10)),
        ft.Divider(height=1),
        main_content
    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)