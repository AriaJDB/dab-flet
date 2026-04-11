import flet as ft
from services.table_service import obtener_tablas, crear_tabla, eliminar_tabla

def get_tablas_ui(db_sel, es_admin, permisos, tiene_acceso, ir_a_nivel, get_style, cache, page, datos_filtrados=None):
    controls = []
    data = datos_filtrados if datos_filtrados is not None else obtener_tablas(db_sel)
    if datos_filtrados is None: cache["datos"] = data

    if es_admin or "CREATE" in permisos:
        input_t = ft.TextField(label="Nombre Tabla", width=250, height=45, border_radius=10, text_size=14)
        cols_ui = ft.Column(spacing=5)
        def add_col(e):
            cols_ui.controls.append(ft.Row([
                ft.TextField(label="Columna", width=150, height=40, text_size=13),
                ft.Dropdown(width=120, height=40, value="VARCHAR(50)", text_size=12, options=[
                    ft.dropdown.Option("INT"), ft.dropdown.Option("VARCHAR(50)"), 
                    ft.dropdown.Option("DATE"), ft.dropdown.Option("BOOLEAN"), ft.dropdown.Option("FLOAT")
                ]),
                ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="red", icon_size=18, 
                             on_click=lambda e: [cols_ui.controls.remove(e.control.parent), page.update()])
            ]))
            page.update()

        controls.append(ft.Container(content=ft.Column([
            ft.Text("Diseñar Tabla", weight="bold", size=16),
            ft.Row([input_t, ft.ElevatedButton("Añadir Columna", icon=ft.Icons.ADD, on_click=add_col)]),
            cols_ui,
            ft.ElevatedButton("Guardar Tabla", bgcolor=ft.Colors.BLUE_700, color="white", 
                on_click=lambda e: [crear_tabla(db_sel, input_t.value, [{"nombre": r.controls[0].value, "tipo": r.controls[1].value} for r in cols_ui.controls if r.controls[0].value]), ir_a_nivel("tablas", db_sel)])
        ], spacing=10), **get_style(), padding=15))

    list_items = []
    for i, t in enumerate(data):
        if tiene_acceso(t) or es_admin:
            list_items.append(ft.ListTile(
                leading=ft.Icon(ft.Icons.TABLE_CHART_OUTLINED, color=ft.Colors.AMBER_400, size=20),
                title=ft.Text(t, weight="w500", size=15),
                on_click=lambda e, n=t: ir_a_nivel("datos", n),
                trailing=ft.IconButton(ft.Icons.DELETE_FOREVER, icon_color="red", icon_size=18, visible=es_admin,
                                     on_click=lambda e, n=t: [eliminar_tabla(db_sel, n), ir_a_nivel("tablas", db_sel)])
            ))
            if i < len(data) - 1: list_items.append(ft.Divider(height=1, thickness=1))

    controls.append(ft.Container(content=ft.Column(list_items, spacing=0), **get_style(), padding=5))
    return controls