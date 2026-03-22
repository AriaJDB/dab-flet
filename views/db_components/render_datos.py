import flet as ft
from services.table_service import obtener_columnas, obtener_datos, eliminar_registro, insertar_registro

def get_datos_ui(db, tabla, es_admin, permisos, ir_a_nivel, get_style, cache, page, datos_filtrados=None):
    controls = []
    cols_raw = obtener_columnas(db, tabla)
    data = datos_filtrados if datos_filtrados is not None else obtener_datos(db, tabla)
    if datos_filtrados is None: cache["datos"] = data

    def abrir_modal_insertar(e):
        campos_input = {}
        columnas_layout = ft.Column(spacing=15, tight=True, scroll=ft.ScrollMode.ADAPTIVE)

        for col in cols_raw:
            nombre_col = col[0]
            tipo_col = col[1].upper() # Aseguramos mayúsculas para comparar
            
            # --- Lógica por Tipo de Dato ---
            
            # 1. ENTEROS (INT)
            if "INT" in tipo_col:
                input_ctrl = ft.TextField(
                    label=f"{nombre_col} (Entero)",
                    input_filter=ft.NumbersOnlyInputFilter(), # Solo números
                    keyboard_type=ft.KeyboardType.NUMBER
                )
            
            elif "VARCHAR" in tipo_col:
                input_ctrl = ft.TextField(
                    label=f"{nombre_col} (Max 50)",
                    max_length=50,
                )
            
            elif "DATE" in tipo_col:
                tf_fecha = ft.TextField(label=f"{nombre_col} (YYYY-MM-DD)", read_only=True, expand=True)
                
                def confirmar_fecha(e_date):
                    if e_date.control.value:
                        tf_fecha.value = e_date.control.value.strftime('%Y-%m-%d')
                        page.update()

                datepicker = ft.DatePicker(
                    on_change=confirmar_fecha,
                )
                page.overlay.append(datepicker)
                
                def abrir_picker(e):
                    datepicker.open = True
                    page.update()

                input_ctrl = ft.Row([
                    tf_fecha,
                    ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=abrir_picker)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                
                input_ctrl.data = tf_fecha

            elif "BOOL" in tipo_col or "TINYINT(1)" in tipo_col:
                input_ctrl = ft.Switch(label=f"{nombre_col} (Falso/Verdadero)", value=False)

            elif "FLOAT" in tipo_col or "DECIMAL" in tipo_col:
                input_ctrl = ft.TextField(
                    label=f"{nombre_col} (Decimal)",
                    input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string="")
                )
            
            else:
                input_ctrl = ft.TextField(label=f"{nombre_col} ({tipo_col})")

            campos_input[nombre_col] = input_ctrl
            columnas_layout.controls.append(input_ctrl)

        def guardar_nuevo_registro(e):
            dict_final = {}
            for nom, ctrl in campos_input.items():
                if isinstance(ctrl, ft.Row):
                    dict_final[nom] = ctrl.data.value
                elif isinstance(ctrl, ft.Switch):
                    dict_final[nom] = 1 if ctrl.value else 0
                else:
                    dict_final[nom] = ctrl.value

            try:
                insertar_registro(db, tabla, dict_final)
                dialogo.open = False
                page.update()
                ir_a_nivel("datos", tabla)
            except Exception as ex:
                print(f"Error: {ex}")

        dialogo = ft.AlertDialog(
            title=ft.Text(f"Nuevo Registro en {tabla}", weight="bold"),
            content=ft.Container(content=columnas_layout, width=400, padding=10),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: [setattr(dialogo, "open", False), page.update()]),
                ft.ElevatedButton("Guardar", bgcolor=ft.Colors.BLUE_700, color="white", on_click=guardar_nuevo_registro)
            ],
        )
        
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    controls.append(ft.Row([
        ft.ElevatedButton(
            "Insertar Fila", 
            icon=ft.Icons.ADD, 
            visible=es_admin or "INSERT" in permisos,
            on_click=abrir_modal_insertar
        ),
        ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: ir_a_nivel("datos", tabla))
    ]))

    if data:
        columns = [ft.DataColumn(ft.Text(c[0], weight="bold", size=13)) for c in cols_raw]
        if es_admin: columns.append(ft.DataColumn(ft.Text("Acciones", weight="bold")))

        rows = []
        for fila in data:
            cells = [ft.DataCell(ft.Text(str(v), size=13)) for v in fila]
            if es_admin:
                cells.append(ft.DataCell(
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE, 
                        icon_color="red", 
                        icon_size=18,
                        on_click=lambda e, f=fila: [eliminar_registro(db, tabla, f[0]), ir_a_nivel("datos", tabla)]
                    )
                ))
            rows.append(ft.DataRow(cells=cells))

        dt = ft.DataTable(heading_row_color="black12", columns=columns, rows=rows)
        controls.append(ft.Container(content=ft.Row([dt], scroll="always"), **get_style(), padding=10))
    else:
        controls.append(ft.Text("Sin registros.", italic=True))
    
    return controls