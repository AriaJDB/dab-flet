import flet as ft
from services.db_service import obtener_bases, crear_base, eliminar_base
from services.table_service import (
    obtener_tablas, obtener_columnas, obtener_datos, 
    crear_tabla, eliminar_tabla, insertar_registro, eliminar_registro
)

def db_view(page: ft.Page):
    estado = {"nivel": "bases", "db_seleccionada": None, "tabla_seleccionada": None}

    # --- UI Estática ---
    txt_mensaje = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    msg_container = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.INFO_OUTLINE, size=20), txt_mensaje], spacing=10),
        padding=10, border_radius=8, visible=False, margin=ft.margin.only(bottom=10)
    )
    breadcrumb_row = ft.Row(spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER)
    main_content = ft.Column(spacing=20, scroll=ft.ScrollMode.ADAPTIVE)

    def mostrar_alerta(msg, es_error=True):
        txt_mensaje.value = msg
        msg_container.visible = True
        msg_container.bgcolor = ft.Colors.RED_50 if es_error else ft.Colors.BLUE_50
        txt_mensaje.color = ft.Colors.RED_700 if es_error else ft.Colors.BLUE_700
        page.update()

    def ir_a_nivel(nivel, nombre=None):
        msg_container.visible = False
        estado["nivel"] = nivel
        if nivel == "bases":
            estado["db_seleccionada"], estado["tabla_seleccionada"] = None, None
            render_bases()
        elif nivel == "tablas":
            if nombre: estado["db_seleccionada"] = nombre
            estado["tabla_seleccionada"] = None
            render_tablas()
        elif nivel == "datos":
            if nombre: estado["tabla_seleccionada"] = nombre
            render_datos()
        
        # Actualizar Breadcrumbs
        breadcrumb_row.controls.clear()
        breadcrumb_row.controls.append(ft.TextButton("Bases", on_click=lambda _: ir_a_nivel("bases")))
        if estado["db_seleccionada"]:
            breadcrumb_row.controls.extend([ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16), ft.TextButton(estado["db_seleccionada"], on_click=lambda _: ir_a_nivel("tablas"))])
        if estado["tabla_seleccionada"]:
            breadcrumb_row.controls.extend([ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16), ft.Text(estado["tabla_seleccionada"], weight="bold")])
        page.update()

    # --- NIVEL 1: BASES ---
    def render_bases():
        main_content.controls.clear()
        input_db = ft.TextField(label="Nombre de nueva Base", width=300)
        
        main_content.controls.append(ft.Row([
            input_db, 
            ft.ElevatedButton("Crear", on_click=lambda _: [crear_base(input_db.value), mostrar_alerta("Base creada. Refrescar.", False)]),
            ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: render_bases())
        ]))
        
        for db in obtener_bases():
            main_content.controls.append(ft.ListTile(
                leading=ft.Icon(ft.Icons.STORAGE, color=ft.Colors.BLUE_700), title=ft.Text(db),
                on_click=lambda e, n=db: ir_a_nivel("tablas", n),
                trailing=ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda e, n=db: [eliminar_base(n), render_bases()])
            ))
        page.update()

    # --- NIVEL 2: TABLAS (CON FORMULARIO RECUPERADO) ---
    def render_tablas():
        main_content.controls.clear()
        db = estado["db_seleccionada"]
        
        input_t = ft.TextField(label="Nombre de la Tabla", width=250)
        cols_ui = ft.Column()

        def add_col(e):
            cols_ui.controls.append(ft.Row([
                ft.TextField(label="Columna", width=150),
                ft.Dropdown(width=120, value="VARCHAR(50)", options=[ft.dropdown.Option("INT"), ft.dropdown.Option("VARCHAR(50)"), ft.dropdown.Option("TEXT")])
            ]))
            page.update()

        def on_guardar_t(e):
            try:
                cols = [{"nombre": r.controls[0].value, "tipo": r.controls[1].value} for r in cols_ui.controls if r.controls[0].value]
                crear_tabla(db, input_t.value, cols)
                mostrar_alerta(f"Tabla '{input_t.value}' creada. Refrescar.", False)
            except Exception as ex: mostrar_alerta(f"Error: {ex}")

        # Formulario de creación
        main_content.controls.append(ft.Card(ft.Container(padding=15, content=ft.Column([
            ft.Text("Nueva Tabla", weight="bold"),
            ft.Row([input_t, ft.ElevatedButton("Añadir Columna", on_click=add_col)]),
            cols_ui,
            ft.Row([
                ft.ElevatedButton("Guardar Tabla", bgcolor=ft.Colors.BLUE_700, color="white", on_click=on_guardar_t),
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: render_tablas())
            ])
        ]))))

        # Lista de tablas
        for t in obtener_tablas(db):
            main_content.controls.append(ft.ListTile(
                leading=ft.Icon(ft.Icons.TABLE_CHART,color=ft.Colors.BLUE_700), title=ft.Text(t),
                on_click=lambda e, n=t: ir_a_nivel("datos", n),
                trailing=ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red", on_click=lambda e, n=t: [eliminar_tabla(db, n), render_tablas()])
            ))
        page.update()

    # --- NIVEL 3: REGISTROS (LÓGICA DE ALERTA CORREGIDA) ---
    def render_datos():
        main_content.controls.clear()
        db, tabla = estado["db_seleccionada"], estado["tabla_seleccionada"]

        def abrir_modal_registro(e):
            columnas = obtener_columnas(db, tabla)
            inputs = {}
            form_fields = ft.Column(spacing=10, tight=True)
            for col in columnas:
                if col[0].lower() == 'id': continue
                tf = ft.TextField(label=col[0], width=300)
                inputs[col[0]] = tf
                form_fields.controls.append(tf)

            def guardar_datos(e):
                try:
                    data = {k: v.value for k, v in inputs.items()}
                    # Forzamos la ejecución
                    insertar_registro(db, tabla, data)
                    
                    # Si llega aquí sin excepción, es éxito
                    dlg.open = False
                    page.update()
                    render_datos()
                    mostrar_alerta("Registro guardado exitosamente ✅", False)
                except Exception as ex:
                    mostrar_alerta(f"Error al insertar: {ex}")

            dlg = ft.AlertDialog(
                title=ft.Text("Nuevo Registro"),
                content=form_fields,
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: [setattr(dlg, "open", False), page.update()]),
                    ft.ElevatedButton("Guardar", on_click=guardar_datos)
                ]
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        main_content.controls.append(ft.Row([
            ft.ElevatedButton("Agregar Fila", icon=ft.Icons.ADD, on_click=abrir_modal_registro),
            ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: render_datos())
        ]))

        try:
            cols = obtener_columnas(db, tabla)
            res = obtener_datos(db, tabla)
            
            columnas_dt = [ft.DataColumn(ft.Text(c[0])) for c in cols]
            columnas_dt.append(ft.DataColumn(ft.Text("Eliminar")))

            filas_dt = []
            for fila in res:
                celdas = [ft.DataCell(ft.Text(str(v))) for v in fila]
                id_val = fila[0] 
                celdas.append(ft.DataCell(
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red", 
                                  on_click=lambda e, id_r=id_val: [eliminar_registro(db, tabla, id_r), render_datos()])
                ))
                filas_dt.append(ft.DataRow(cells=celdas))

            main_content.controls.append(ft.Row([ft.DataTable(columns=columnas_dt, rows=filas_dt)], scroll=ft.ScrollMode.ALWAYS))
        except Exception as e: mostrar_alerta(f"Error: {e}")
        page.update()

    ir_a_nivel("bases")
    return ft.Column([
        ft.Container(content=ft.Column([breadcrumb_row, msg_container, ft.Divider(height=1)]), padding=10),
        ft.Container(content=main_content, expand=True, padding=10)
    ], expand=True)