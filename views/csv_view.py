import flet as ft
from services.csv_service import exportar_csv, importar_csv
from services.db_service import obtener_bases
from services.table_service import obtener_tablas
import tkinter as tk
from tkinter import filedialog
import threading
import os

def csv_view(page: ft.Page):

    # --- ESTILOS ---
    bg_color = ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE
    card_shadow = ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)

    # --- MENSAJES SUAVES ---
    txt_mensaje = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    icono_msg = ft.Icon(ft.Icons.INFO_OUTLINE, size=20)

    msg_container = ft.Container(
        content=ft.Row([icono_msg, txt_mensaje], spacing=10),
        padding=10,
        border_radius=8,
        visible=False,
        margin=ft.margin.only(bottom=10)
    )

    def mostrar_alerta(msg, es_error=True):
        txt_mensaje.value = msg
        msg_container.visible = True

        if es_error:
            msg_container.bgcolor = ft.Colors.RED_50
            txt_mensaje.color = ft.Colors.RED_700
            icono_msg.name = ft.Icons.ERROR_OUTLINE
            icono_msg.color = ft.Colors.RED_700
        else:
            msg_container.bgcolor = ft.Colors.GREEN_50
            txt_mensaje.color = ft.Colors.GREEN_700
            icono_msg.name = ft.Icons.CHECK_CIRCLE_OUTLINE
            icono_msg.color = ft.Colors.GREEN_700

        page.update()

    # --- ESTADO ---
    tabla_seleccionada = {"valor": None}
    tablas_originales = []

    # --- CONTROLES ---
    dropdown_db = ft.Dropdown(label="Seleccionar Base de Datos", width=350, border_radius=10)

    search_tablas = ft.TextField(
        label="Buscar tabla...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        on_change=lambda e: filtrar_tablas(e.control.value)
    )

    contador_tablas = ft.Text("", size=12, color=ft.Colors.GREY_600)

    list_tablas = ft.Column(spacing=8, height=250, scroll=ft.ScrollMode.AUTO)

    ruta_export = ft.TextField(label="Carpeta de destino", read_only=True, expand=True, border_radius=10)
    ruta_import = ft.TextField(label="Archivo .csv", read_only=True, expand=True, border_radius=10)
    nombre_export = ft.TextField(label="Nombre del archivo final", width=350, border_radius=10)

    # --- RENDER TABLAS ---
    def render_tablas(lista):
        list_tablas.controls.clear()

        for t in lista:
            seleccionado = tabla_seleccionada["valor"] == t

            list_tablas.controls.append(
                ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(t),
                        leading=ft.Icon(ft.Icons.TABLE_CHART,color=ft.Colors.YELLOW_700),
                        trailing=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.BLUE_700) if seleccionado else None,
                        on_click=lambda e, tabla=t: seleccionar_tabla(tabla)
                    ),
                    border_radius=12,
                    padding=5,
                    bgcolor=ft.Colors.BLUE_50 if seleccionado else None,
                    border=ft.border.all(
                        1,
                        ft.Colors.BLUE_300 if seleccionado else ft.Colors.GREY_300
                    )
                )
            )

        contador_tablas.value = f"{len(lista)} tabla(s)"
        list_tablas.update()
        contador_tablas.update()

    # --- FILTRO ---
    def filtrar_tablas(texto):
        if not texto:
            render_tablas(tablas_originales)
            return

        filtradas = [t for t in tablas_originales if texto.lower() in t.lower()]
        render_tablas(filtradas)

    # --- SELECCIÓN ---
    def seleccionar_tabla(tabla):
        tabla_seleccionada["valor"] = tabla
        render_tablas(tablas_originales)
        mostrar_alerta(f"Tabla seleccionada: {tabla}", False)

    # --- CARGAR TABLAS ---
    def cargar_tablas_click(e):
        db = dropdown_db.value

        if not db:
            mostrar_alerta("Selecciona una base primero")
            return

        try:
            tablas = obtener_tablas(db)

            print("Tablas:", tablas)

            tablas_originales.clear()
            tablas_originales.extend(tablas)
            tabla_seleccionada["valor"] = None

            if not tablas:
                render_tablas([])
                mostrar_alerta("No se encontraron tablas")
                return

            render_tablas(tablas_originales)
            mostrar_alerta(f"{len(tablas)} tablas cargadas", False)

        except Exception as ex:
            mostrar_alerta(f"Error: {ex}")

    # --- FILE PICKER ---
    def seleccionar_path(tipo):
        def abrir():
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            if tipo == "carpeta":
                res = filedialog.askdirectory()
                if res:
                    ruta_export.value = res
            else:
                res = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
                if res:
                    ruta_import.value = res

            page.update()
            root.destroy()

        threading.Thread(target=abrir, daemon=True).start()

    # --- ACCIONES ---
    def ejecutar_exportar(e):
        tabla = tabla_seleccionada["valor"]

        if not all([dropdown_db.value, tabla, ruta_export.value, nombre_export.value]):
            mostrar_alerta("Faltan datos")
            return

        path = os.path.join(ruta_export.value, f"{nombre_export.value}.csv")

        if exportar_csv(dropdown_db.value, tabla, path):
            mostrar_alerta("Exportado correctamente", False)

    def ejecutar_importar(e):
        tabla = tabla_seleccionada["valor"]

        if not all([dropdown_db.value, tabla, ruta_import.value]):
            mostrar_alerta("Faltan datos")
            return

        if importar_csv(dropdown_db.value, tabla, ruta_import.value):
            mostrar_alerta("Importado correctamente", False)

    # --- CARGAR BASES ---
    try:
        bases = obtener_bases()
        dropdown_db.options = [ft.dropdown.Option(b) for b in bases]
    except:
        pass

    # --- UI ---
    return ft.Column([
        ft.Text("Intercambio de Datos (CSV)", size=28, weight="bold"),
        msg_container,

        # SELECTOR
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.STORAGE_ROUNDED, color=ft.Colors.BLUE_700),
                    dropdown_db,
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        on_click=cargar_tablas_click
                    )
                ]),
                search_tablas,
                contador_tablas,
                list_tablas
            ], spacing=15),
            padding=20,
            bgcolor=bg_color,
            border_radius=15,
            shadow=card_shadow
        ),

        ft.Row([
            # CARD EXPORTAR (ORIGINAL)
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.FILE_DOWNLOAD, color=ft.Colors.BLUE_800),
                        ft.Text("Exportar", weight="bold")
                    ]),
                    ft.Divider(),
                    ft.Row([
                        ruta_export,
                        ft.IconButton(icon=ft.Icons.FOLDER_OPEN, on_click=lambda _: seleccionar_path("carpeta"))
                    ]),
                    nombre_export,
                    ft.ElevatedButton(
                        "Exportar CSV",
                        on_click=ejecutar_exportar,
                        bgcolor=ft.Colors.BLUE_700,
                        color="white",
                        width=200
                    )
                ], spacing=15),
                expand=True,
                padding=25,
                bgcolor=bg_color,
                border_radius=15,
                shadow=card_shadow,
                border=ft.Border(top=ft.BorderSide(5, ft.Colors.BLUE_700))
            ),

            # CARD IMPORTAR (ORIGINAL)
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.FILE_UPLOAD, color=ft.Colors.GREEN_800),
                        ft.Text("Importar", weight="bold")
                    ]),
                    ft.Divider(),
                    ft.Row([
                        ruta_import,
                        ft.IconButton(icon=ft.Icons.ATTACH_FILE, on_click=lambda _: seleccionar_path("archivo"))
                    ]),
                    ft.Divider(height=45, color=ft.Colors.TRANSPARENT),
                    ft.ElevatedButton(
                        "Importar CSV",
                        on_click=ejecutar_importar,
                        bgcolor=ft.Colors.GREEN_700,
                        color="white",
                        width=200
                    )
                ], spacing=15),
                expand=True,
                padding=25,
                bgcolor=bg_color,
                border_radius=15,
                shadow=card_shadow,
                border=ft.Border(top=ft.BorderSide(5, ft.Colors.GREEN_700))
            ),
        ], spacing=20)

    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)