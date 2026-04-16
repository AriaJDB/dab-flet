import flet as ft
from services.db_service import obtener_bases, crear_base, eliminar_base

def get_bases_ui(es_admin, tiene_acceso, ir_a_nivel, mostrar_alerta, get_style, cache_manager,session_data, datos_filtrados=None):
    controls = []
    
    if datos_filtrados is None:
        data = obtener_bases(session_data)
        cache_manager["datos"] = data
    else:
        data = datos_filtrados

    if es_admin:
        input_db = ft.TextField(label="Nueva Base", width=300, height=45, border_radius=10)
        
        def validar_y_crear(e):
            if not input_db.value.strip():
                mostrar_alerta("El nombre de la base no puede estar vacío")
                return
            crear_base(input_db.value)
            ir_a_nivel("bases")
            mostrar_alerta("Base creada", False)

        controls.append(ft.Row([
            input_db, 
            ft.ElevatedButton("Crear", icon=ft.Icons.ADD, on_click=validar_y_crear)
        ]))
    
    list_items = []
    for i, db in enumerate(data):
        if tiene_acceso(db) or db == "information_schema":
            list_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.STORAGE_ROUNDED, color=ft.Colors.BLUE_400),
                    title=ft.Text(db, weight="w500"),
                    on_click=lambda e, n=db: ir_a_nivel("tablas", n),
                    trailing=ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red", visible=es_admin,
                        on_click=lambda e, n=db: [eliminar_base(n), ir_a_nivel("bases")])
                )
            )
            if i < len(data) - 1: list_items.append(ft.Divider(height=1))

    controls.append(ft.Container(content=ft.Column(list_items, spacing=0), **get_style(), padding=5))
    return controls