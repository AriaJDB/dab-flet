import flet as ft
from services.db_service import obtener_bases, crear_base, eliminar_base
from services.table_service import obtener_tablas

def db_view(page: ft.Page):

    lista = ft.Column()
    detalle = ft.Column()
    input_db = ft.TextField(label="Nombre de la base", width=300)

    # 🔄 Cargar bases
    def cargar():
        lista.controls.clear()
        detalle.controls.clear()

        bases = obtener_bases()

        for db in bases:
            lista.controls.append(
                ft.ListTile(
                    title=ft.Text(db),
                    on_click=lambda e, nombre=db: ver_db(nombre),
                    trailing=ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color="red",
                        on_click=lambda e, nombre=db: eliminar(nombre)
                    )
                )
            )

        page.update()

    # 👁️ Ver tablas de la base
    def ver_db(nombre):
        detalle.controls.clear()

        tablas = obtener_tablas(nombre)

        detalle.controls.append(ft.Text(f"Base: {nombre}", size=20))
        detalle.controls.append(ft.Text("Tablas:", weight="bold"))

        for t in tablas:
            detalle.controls.append(ft.Text(f"• {t}"))

        page.update()

    def crear(e):
        if input_db.value:
            crear_base(input_db.value)
            input_db.value = ""
            cargar()

    def eliminar(nombre):
        eliminar_base(nombre)
        cargar()

    cargar()

    return ft.Column(
        [
            ft.Text("📦 Bases de Datos", size=24, weight="bold"),

            ft.Row([
                input_db,
                ft.ElevatedButton("Crear", on_click=crear)
            ]),

            ft.Divider(),

            ft.Row(
                [
                    ft.Container(lista, width=300, height=350, border=ft.border.all(1)),
                    ft.Container(detalle, expand=True, height=350, border=ft.border.all(1))
                ]
            )
        ]
    )