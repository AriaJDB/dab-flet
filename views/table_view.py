import flet as ft
from services.table_service import *
from services.db_service import obtener_bases

def table_view(page: ft.Page):
    # --- Contenedores Dinámicos ---
    lista_tablas = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=5)
    columnas_inputs = ft.Column(spacing=10)
    formulario_registro = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=15)

    # --- Elementos de UI ---
    dropdown_db = ft.Dropdown(
        label="Seleccionar Base de Datos",
        width=300,
        border_radius=10,
        # ❌ Borra la línea de on_change de aquí adentro
    )
    
    # ✅ Asígnale el evento justo después de crearlo
    dropdown_db.on_change = lambda e: cargar_tablas()

    input_tabla_nueva = ft.TextField(
        label="Nombre de la nueva tabla",
        hint_text="Ej: productos",
        width=300,
        border_radius=10
    )

    tabla_actual = {"nombre": None}
    TIPOS = ["INT", "VARCHAR(50)", "TEXT", "DATE", "FLOAT"]

    # 🔄 Cargar bases al inicio
    def cargar_bases():
        try:
            bases = obtener_bases()
            dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
            page.update()
        except Exception as e:
            print(f"Error bases: {e}")

    # 🔄 Listar tablas de la DB seleccionada
    def cargar_tablas():
        lista_tablas.controls.clear()
        formulario_registro.controls.clear()
        
        db = dropdown_db.value
        if not db: return

        try:
            tablas = obtener_tablas(db)
            for t in tablas:
                lista_tablas.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.TABLE_ROWS_ROUNDED, color=ft.Colors.BLUE_400, size=20),
                            ft.Text(t, weight=ft.FontWeight.W_500, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                                icon_color=ft.Colors.RED_400,
                                on_click=lambda e, nombre=t: eliminar(nombre)
                            )
                        ]),
                        padding=ft.Padding.symmetric(horizontal=15, vertical=8),
                        border_radius=8,
                        on_click=lambda e, nombre=t: seleccionar_tabla(nombre),
                        on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.BLACK12 if e.data == "true" else None) or e.control.update()
                    )
                )
        except Exception as e:
            lista_tablas.controls.append(ft.Text(f"Error: {e}", color="red"))
        
        page.update()

    # 🎯 Generar formulario dinámico para insertar
    def seleccionar_tabla(nombre):
        formulario_registro.controls.clear()
        tabla_actual["nombre"] = nombre
        db = dropdown_db.value
        
        formulario_registro.controls.append(
            ft.Text(f"Nuevo Registro en: {nombre}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        )

        try:
            columnas = obtener_columnas(db, nombre)
            inputs_dict = {}

            for col in columnas:
                col_nombre = col[0]
                if col_nombre.lower() == "id": continue 

                campo = ft.TextField(
                    label=col_nombre.capitalize(),
                    border_radius=8,
                    focused_border_color=ft.Colors.BLUE_400
                )
                inputs_dict[col_nombre] = campo
                formulario_registro.controls.append(campo)

            def guardar_registro(e):
                valores = {k: v.value for k, v in inputs_dict.items()}
                if any(not v for v in valores.values()):
                    page.open(ft.SnackBar(ft.Text("Por favor, llena todos los campos")))
                    return

                try:
                    insertar_registro(db, nombre, valores)
                    for c in inputs_dict.values(): c.value = ""
                    page.open(ft.SnackBar(ft.Text("¡Registro guardado exitosamente! ✅")))
                    page.update()
                except Exception as ex:
                    page.open(ft.SnackBar(ft.Text(f"Error: {ex}")))

            formulario_registro.controls.append(
                ft.Button(
                    "Guardar Registro",
                    icon=ft.Icons.SAVE_ROUNDED,
                    on_click=guardar_registro,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
                )
            )
        except Exception as e:
            formulario_registro.controls.append(ft.Text(f"Error al leer columnas: {e}"))
        
        page.update()

    # ➕ Lógica de creación de tabla
    def agregar_fila_columna(e):
        nombre_col = ft.TextField(label="Nombre Columna", expand=True, border_radius=8)
        tipo_col = ft.Dropdown(
            label="Tipo",
            width=150,
            border_radius=8,
            options=[ft.dropdown.Option(t) for t in TIPOS],
            value="VARCHAR(50)"
        )
        columnas_inputs.controls.append(ft.Row([nombre_col, tipo_col], spacing=10))
        page.update()

    def ejecutar_creacion(e):
        db = dropdown_db.value
        nombre_t = input_tabla_nueva.value
        cols_data = []

        for row in columnas_inputs.controls:
            if row.controls[0].value:
                cols_data.append({"nombre": row.controls[0].value, "tipo": row.controls[1].value})

        if db and nombre_t and cols_data:
            crear_tabla(db, nombre_t, cols_data)
            input_tabla_nueva.value = ""
            columnas_inputs.controls.clear()
            cargar_tablas()
            page.open(ft.SnackBar(ft.Text(f"Tabla '{nombre_t}' creada")))

    def eliminar(nombre):
        eliminar_tabla(dropdown_db.value, nombre)
        cargar_tablas()

    cargar_bases()

    # --- DISEÑO FINAL ---
    return ft.Column([
        # Header
        ft.Row([
            ft.Column([
                ft.Text("Gestión de Tablas", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Crea tablas o inserta datos rápidamente", color=ft.Colors.BLUE_GREY_400),
            ], expand=True),
            dropdown_db
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

        ft.Row([
            # IZQUIERDA: Creación y Lista
            ft.Column([
                # Card 1: Crear Tabla
                ft.Container(
                    content=ft.Column([
                        ft.Text("Diseñar Nueva Tabla", weight=ft.FontWeight.BOLD),
                        input_tabla_nueva,
                        ft.Button("Añadir Columna", icon=ft.Icons.ADD, on_click=agregar_fila_columna),
                        columnas_inputs,
                        ft.Button("Crear Tabla Ahora", on_click=ejecutar_creacion, 
                                  style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)),
                    ], spacing=15),
                    padding=20, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE, border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
                ),
                # Card 2: Lista de Tablas
                ft.Container(
                    content=ft.Column([
                        ft.Text("Tablas Existentes", weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        lista_tablas
                    ]),
                    expand=True, padding=20, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE, border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
                )
            ], width=350, spacing=20),

            # DERECHA: Formulario Dinámico
            ft.Container(
                content=formulario_registro,
                expand=True,
                padding=30,
                bgcolor=ft.Colors.GREY_50,
                border_radius=15,
                border=ft.Border(left=ft.BorderSide(2, ft.Colors.BLUE_100))
            )
        ], expand=True, spacing=20)
    ], expand=True)