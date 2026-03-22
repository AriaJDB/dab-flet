import flet as ft
from services.db_service import obtener_bases, crear_base, eliminar_base
from services.table_service import obtener_tablas

def db_view(page: ft.Page):
    # --- Contenedores de datos ---
    lista_bases = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
    detalle_tablas = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
    
    # --- Inputs Estilizados ---
    input_db = ft.TextField(
        label="Nueva Base de Datos",
        hint_text="Ej: ventas_2026", # ✅ Cambiado de placeholder a hint_text
        width=400,
        border_radius=10,
        prefix_icon=ft.Icons.ADD_OUTLINED,
        text_size=14
    )

    # 🔄 Cargar bases de datos
    def cargar_lista():
        lista_bases.controls.clear()
        detalle_tablas.controls.clear()
        
        try:
            bases = obtener_bases()
            for db in bases:
                lista_bases.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DATA_ARRAY_ROUNDED, color=ft.Colors.BLUE_400),
                            ft.Text(db, weight=ft.FontWeight.W_500, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.RED_400,
                                tooltip="Eliminar Base",
                                on_click=lambda e, nombre=db: eliminar(nombre)
                            )
                        ]),
                        padding=ft.Padding.all(15),
                        border_radius=10,
                        bgcolor=ft.Colors.GREY_50,
                        on_click=lambda e, nombre=db: ver_tablas_de_db(nombre),
                        on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.BLUE_50 if e.data == "true" else ft.Colors.GREY_50) or e.control.update()
                    )
                )
        except Exception as ex:
            lista_bases.controls.append(ft.Text(f"Error al cargar: {ex}", color="red"))
        
        page.update()

    # 👁️ Ver tablas de la base seleccionada
    def ver_tablas_de_db(nombre):
        detalle_tablas.controls.clear()
        
        # Encabezado del detalle
        detalle_tablas.controls.append(
            ft.Row([
                ft.Icon(ft.Icons.STORAGE_ROUNDED, color=ft.Colors.BLUE_700),
                ft.Text(f"Tablas en: {nombre}", size=18, weight=ft.FontWeight.BOLD)
            ])
        )
        detalle_tablas.controls.append(ft.Divider(height=10, color=ft.Colors.TRANSPARENT))

        try:
            tablas = obtener_tablas(nombre)
            if not tablas:
                detalle_tablas.controls.append(ft.Text("No hay tablas en esta base.", italic=True, color=ft.Colors.BLUE_GREY_400))
            
            for t in tablas:
                detalle_tablas.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.TABLE_CHART_OUTLINED, size=18, color=ft.Colors.BLUE_GREY_400),
                            ft.Text(t, size=14)
                        ]),
                        padding=ft.Padding.symmetric(vertical=5, horizontal=10)
                    )
                )
        except Exception as ex:
            detalle_tablas.controls.append(ft.Text(f"Error: {ex}", color="red"))

        page.update()

    def crear(e):
        if input_db.value:
            crear_base(input_db.value)
            input_db.value = ""
            cargar_lista()

    def eliminar(nombre):
        # Aquí podrías agregar un ConfirmDialog de Flet para hacerlo más profesional
        eliminar_base(nombre)
        cargar_lista()

    # Carga inicial
    cargar_lista()

    # --- Estructura Visual Final ---
    return ft.Column(
        [
            # Título y Acción de Crear
            ft.Row([
                ft.Column([
                    ft.Text("Bases de Datos", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Gestión y visualización de esquemas", color=ft.Colors.BLUE_GREY_400),
                ], expand=True),
                ft.Row([
                    input_db,
                    ft.Button(
                        "Crear Base",
                        icon=ft.Icons.ADD,
                        on_click=crear,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_700,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    )
                ], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            ft.Divider(height=40, color=ft.Colors.TRANSPARENT),

            # Cuerpo: Lista y Detalle
            ft.Row(
                [
                    # Columna Izquierda: Lista de Bases
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Bases Disponibles", weight=ft.FontWeight.BOLD),
                            ft.Divider(height=10),
                            lista_bases
                        ]),
                        width=350,
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                        expand=False
                    ),

                    # Columna Derecha: Detalle de Tablas
                    ft.Container(
                        content=detalle_tablas,
                        expand=True,
                        padding=20,
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=15,
                        border=ft.Border(
                            left=ft.BorderSide(1, ft.Colors.BLUE_GREY_100)
                        )
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=20
            )
        ],
        expand=True,
        spacing=0
    )