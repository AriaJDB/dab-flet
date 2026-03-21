import flet as ft
from services.table_service import *
from services.db_service import obtener_bases

def table_view(page: ft.Page):

    lista_tablas = ft.Column()
    columnas_inputs = ft.Column()
    formulario = ft.Column()

    input_tabla = ft.TextField(label="Nombre de la tabla", width=250)
    dropdown_db = ft.Dropdown(label="Selecciona base de datos", width=250)

    tabla_actual = {"nombre": None}

    TIPOS = ["INT", "VARCHAR(50)", "TEXT", "DATE", "FLOAT"]

    # 🔄 Cargar bases
    def cargar_bases():
        bases = obtener_bases()
        dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
        page.update()

    # 🔄 Cargar tablas
    def cargar_tablas(e=None):
        lista_tablas.controls.clear()
        formulario.controls.clear()

        db = dropdown_db.value
        if not db:
            return

        tablas = obtener_tablas(db)

        for t in tablas:
            lista_tablas.controls.append(
                ft.ListTile(
                    title=ft.Text(t),
                    on_click=lambda e, nombre=t: seleccionar_tabla(nombre),
                    trailing=ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color="red",
                        on_click=lambda e, nombre=t: eliminar(nombre)
                    )
                )
            )

        page.update()

    # 🎯 Seleccionar tabla → generar formulario dinámico
    def seleccionar_tabla(nombre):
        formulario.controls.clear()
        tabla_actual["nombre"] = nombre

        db = dropdown_db.value
        columnas = obtener_columnas(db, nombre)

        inputs = {}

        formulario.controls.append(ft.Text(f"Insertar en {nombre}", size=20))

        for col in columnas:
            col_nombre = col[0]

            if col_nombre == "id":
                continue  # skip id auto

            campo = ft.TextField(label=col_nombre)
            inputs[col_nombre] = campo

            formulario.controls.append(campo)

        # ➕ botón insertar
        def insertar(e):
            valores = {}

            for k, campo in inputs.items():
                if not campo.value:
                    page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"))
                    page.snack_bar.open = True
                    page.update()
                    return

                valores[k] = campo.value

            try:
                insertar_registro(db, nombre, valores)

                for campo in inputs.values():
                    campo.value = ""

                page.snack_bar = ft.SnackBar(ft.Text("Registro insertado ✅"))
                page.snack_bar.open = True

                page.update()

            except Exception as e:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"))
                page.snack_bar.open = True
                page.update()

        formulario.controls.append(
            ft.ElevatedButton("Insertar registro", on_click=insertar)
        )

        page.update()

    # ➕ Crear tabla (igual que antes)
    def agregar_columna(e):
        nombre = ft.TextField(label="Nombre", width=150)
        tipo = ft.Dropdown(
            label="Tipo",
            width=180,
            options=[ft.dropdown.Option(t) for t in TIPOS],
            value="INT"
        )
        columnas_inputs.controls.append(ft.Row([nombre, tipo]))
        page.update()

    def crear(e):
        db = dropdown_db.value
        nombre = input_tabla.value

        columnas = []

        for fila in columnas_inputs.controls:
            col_nombre = fila.controls[0].value
            col_tipo = fila.controls[1].value

            if not col_nombre or not col_tipo:
                return

            columnas.append({"nombre": col_nombre, "tipo": col_tipo})

        if db and nombre and columnas:
            crear_tabla(db, nombre, columnas)

            input_tabla.value = ""
            columnas_inputs.controls.clear()

            cargar_tablas()

    def eliminar(nombre):
        db = dropdown_db.value
        eliminar_tabla(db, nombre)
        cargar_tablas()

    dropdown_db.on_change = cargar_tablas

    cargar_bases()

    return ft.Column(
        [
            ft.Text("📊 Gestión de Tablas", size=24, weight="bold"),

            dropdown_db,

            ft.Divider(),

            # crear tabla
            ft.Text("Crear tabla:", weight="bold"),
            input_tabla,
            ft.ElevatedButton("Agregar columna", on_click=agregar_columna),
            columnas_inputs,
            ft.ElevatedButton("Crear tabla", on_click=crear),

            ft.Divider(),

            ft.Row(
                [
                    ft.Container(lista_tablas, width=250, height=300, border=ft.border.all(1)),
                    ft.Container(formulario, expand=True, height=300, border=ft.border.all(1))
                ]
            )
        ]
    )