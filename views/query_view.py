import flet as ft
from services.db_service import obtener_bases
from services.query_service import ejecutar_query

def query_view(page: ft.Page):

    # --- Mensajes estilo consistente con la app ---
    txt_mensaje = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    icono_mensaje = ft.Icon(ft.Icons.INFO_OUTLINE, size=20)

    msg_container = ft.Container(
        content=ft.Row([icono_mensaje, txt_mensaje], spacing=10),
        padding=10,
        border_radius=8,
        visible=False
    )

    def mostrar_alerta(msg, es_error=True):
        msg_container.visible = True
        txt_mensaje.value = msg

        if es_error:
            msg_container.bgcolor = ft.Colors.RED_50
            txt_mensaje.color = ft.Colors.RED_700
            icono_mensaje.name = ft.Icons.ERROR_OUTLINE
            icono_mensaje.color = ft.Colors.RED_700
        else:
            msg_container.bgcolor = ft.Colors.GREEN_50
            txt_mensaje.color = ft.Colors.GREEN_700
            icono_mensaje.name = ft.Icons.CHECK_CIRCLE_OUTLINE
            icono_mensaje.color = ft.Colors.GREEN_700

        page.update()

    # --- Controles ---
    dropdown_db = ft.Dropdown(
        label="Base de Datos",
        width=300,
        border_radius=10
    )

    editor_sql = ft.TextField(
        label="Escribe tu consulta SQL",
        multiline=True,
        min_lines=6,
        max_lines=12,
        border_radius=10,
        expand=True,
        value=""
    )

    resultados_container = ft.Container(expand=True)

    # --- Cargar bases de datos ---
    try:
        bases = obtener_bases()
        dropdown_db.options = [ft.dropdown.Option(db) for db in bases]
    except Exception as e:
        mostrar_alerta(f"Error al cargar bases: {e}")

    # --- Ejecutar Query ---
    def ejecutar(e):
        if not dropdown_db.value:
            mostrar_alerta("Selecciona una base de datos.")
            return

        query = editor_sql.value.strip()
        if not query:
            mostrar_alerta("La consulta está vacía.")
            return

        try:
            resultado = ejecutar_query(dropdown_db.value, query)

            if resultado["tipo"] == "select":
                columnas = resultado["columnas"]
                filas = resultado["filas"]

                tabla = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text(col, weight="bold")) for col in columnas],
                    rows=[
                        ft.DataRow(
                            cells=[ft.DataCell(ft.Text(str(valor))) for valor in fila]
                        ) for fila in filas
                    ],
                    column_spacing=20,
                    heading_row_color=ft.Colors.BLACK12,
                )

                resultados_container.content = ft.Row(
                    [tabla],
                    scroll=ft.ScrollMode.ALWAYS
                )

                mostrar_alerta(f"Consulta ejecutada correctamente. Filas: {len(filas)}", False)

            else:
                resultados_container.content = ft.Container(
                    content=ft.Text(
                        f"Filas afectadas: {resultado['filas_afectadas']}",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    alignment=ft.alignment.center,
                    padding=20
                )
                mostrar_alerta(
                    f"Operación completada. Filas afectadas: {resultado['filas_afectadas']}",
                    False
                )

        except Exception as ex:
            mostrar_alerta(f"Error en la consulta: {ex}")

        page.update()

    # --- Limpiar Editor ---
    def limpiar(e):
        editor_sql.value = ""
        resultados_container.content = None
        msg_container.visible = False
        page.update()

    # --- Diseño ---
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = ft.Colors.SURFACE_CONTAINER_HIGHEST if is_dark else ft.Colors.WHITE

    return ft.Column(
        [
            # Encabezado
            ft.Column([
                ft.Text("Editor SQL", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Ejecuta consultas SQL directamente sobre la base de datos.",
                    color=ft.Colors.BLUE_GREY_400
                ),
                msg_container,
            ]),

            # Editor
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                dropdown_db,
                                ft.ElevatedButton(
                                    "Ejecutar",
                                    icon=ft.Icons.PLAY_ARROW,
                                    on_click=ejecutar,
                                    bgcolor=ft.Colors.BLUE_700,
                                    color="white",
                                ),
                                ft.OutlinedButton(
                                    "Limpiar",
                                    icon=ft.Icons.CLEAR,
                                    on_click=limpiar,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=10,
                        ),
                        editor_sql,
                    ],
                    spacing=15,
                ),
                padding=20,
                bgcolor=card_bg,
                border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
            ),

            # Resultados
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Resultados", weight=ft.FontWeight.BOLD, size=18),
                        ft.Divider(),
                        resultados_container,
                    ],
                    expand=True,
                ),
                padding=20,
                bgcolor=card_bg,
                border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                expand=True,
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
    )