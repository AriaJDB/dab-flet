import flet as ft
from services.metrics_service import (
    obtener_conexiones,
    obtener_queries,
    obtener_threads_running,
    obtener_bytes,
    obtener_slow_queries,
)
import time
import asyncio


def metrics_view(page: ft.Page):
    # 🔁 Si la vista ya existe, simplemente la retornamos
    if hasattr(page, "metrics_view_instance"):
        return page.metrics_view_instance

    # 🧠 Estado global persistente
    if not hasattr(page, "metrics_state"):
        page.metrics_state = {
            "conexiones_data": [],
            "queries_data": [],
            "last_queries": None,
            "last_time": None,
        }

    state = page.metrics_state

    # 🎨 Configuración de tema
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = (
        ft.Colors.SURFACE_CONTAINER_HIGHEST
        if is_dark
        else ft.Colors.WHITE
    )
    text_secondary = ft.Colors.BLUE_GREY_400

    # 📊 Controles de métricas
    conexiones_val = ft.Text("0", size=34, weight=ft.FontWeight.BOLD)
    qps_val = ft.Text("0.0", size=34, weight=ft.FontWeight.BOLD)
    threads_val = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
    bytes_in_val = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
    bytes_out_val = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
    slow_val = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)

    # Guardar referencias para el loop
    page.metrics_controls = {
        "conexiones": conexiones_val,
        "qps": qps_val,
        "threads": threads_val,
        "bytes_in": bytes_in_val,
        "bytes_out": bytes_out_val,
        "slow": slow_val,
    }

    # 📈 Contenedor de gráfica
    chart = ft.Row(
        height=220,
        spacing=3,
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.END,
    )
    page.metrics_controls["chart"] = chart

    # 🧩 Función para crear tarjetas de métricas
    def metric_card(title, value_control, icon, color):
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor=card_bg,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
            content=ft.Row(
                [
                    ft.Icon(icon, size=40, color=color),
                    ft.Column(
                        [
                            ft.Text(title, size=14, color=text_secondary),
                            value_control,
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=15,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # 📊 Función para actualizar la gráfica
    def actualizar_chart():
        chart.controls.clear()
        for i in range(len(state["conexiones_data"])):
            conexiones = state["conexiones_data"][i]
            qps = state["queries_data"][i]

            chart.controls.append(
                ft.Column(
                    [
                        ft.Container(
                            width=6,
                            height=max(2, min(qps * 8, 160)),
                            bgcolor=ft.Colors.GREEN_400,
                            border_radius=2,
                            tooltip=f"QPS: {round(qps, 2)}",
                        ),
                        ft.Container(
                            width=6,
                            height=max(2, min(conexiones * 8, 160)),
                            bgcolor=ft.Colors.BLUE_400,
                            border_radius=2,
                            tooltip=f"Conexiones: {conexiones}",
                        ),
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.END,
                )
            )

    # 🔁 Loop asincrónico único
    async def loop():
        while True:
            try:
                conexiones = obtener_conexiones()
                queries = obtener_queries()
                threads = obtener_threads_running()
                bytes_in, bytes_out = obtener_bytes()
                slow = obtener_slow_queries()

                now = time.time()

                # 📊 Cálculo de QPS
                if state["last_queries"] is not None:
                    delta_q = queries - state["last_queries"]
                    delta_t = now - state["last_time"]
                    qps = delta_q / delta_t if delta_t > 0 else 0
                else:
                    qps = 0

                # 📈 Guardar histórico
                state["conexiones_data"].append(conexiones)
                state["queries_data"].append(qps)
                state["conexiones_data"] = state["conexiones_data"][-40:]
                state["queries_data"] = state["queries_data"][-40:]

                # 🧾 Actualizar UI
                controls = page.metrics_controls
                controls["conexiones"].value = str(conexiones)
                controls["qps"].value = f"{qps:.2f}"
                controls["threads"].value = str(threads)
                controls["bytes_in"].value = f"{bytes_in:,}"
                controls["bytes_out"].value = f"{bytes_out:,}"
                controls["slow"].value = str(slow)

                actualizar_chart()

                state["last_queries"] = queries
                state["last_time"] = now

                page.update()

            except Exception as e:
                print(f"Error en métricas: {e}")

            await asyncio.sleep(2)

    # 🚀 Iniciar el loop solo una vez
    if not hasattr(page, "metrics_task_started"):
        page.run_task(loop)
        page.metrics_task_started = True

    # 🧱 Layout principal
    view = ft.Column(
        [
            ft.Column(
                [
                    ft.Text(
                        "Dashboard de Métricas",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Monitoreo en tiempo real del servidor MariaDB",
                        color=text_secondary,
                    ),
                ]
            ),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

            # KPIs principales
            ft.Row(
                [
                    metric_card(
                        "Conexiones Activas",
                        conexiones_val,
                        ft.Icons.LANGUAGE_ROUNDED,
                        ft.Colors.BLUE_700,
                    ),
                    metric_card(
                        "Queries por Segundo",
                        qps_val,
                        ft.Icons.SPEED_ROUNDED,
                        ft.Colors.GREEN_700,
                    ),
                ],
                spacing=20,
            ),

            # Métricas secundarias
            ft.Row(
                [
                    metric_card(
                        "Threads en Ejecución",
                        threads_val,
                        ft.Icons.SETTINGS,
                        ft.Colors.ORANGE_700,
                    ),
                    metric_card(
                        "Bytes Recibidos",
                        bytes_in_val,
                        ft.Icons.DOWNLOAD,
                        ft.Colors.PURPLE_700,
                    ),
                    metric_card(
                        "Bytes Enviados",
                        bytes_out_val,
                        ft.Icons.UPLOAD,
                        ft.Colors.CYAN_700,
                    ),
                    metric_card(
                        "Slow Queries",
                        slow_val,
                        ft.Icons.WARNING_AMBER_ROUNDED,
                        ft.Colors.RED_700,
                    ),
                ],
                spacing=20,
            ),

            # Gráfica
            ft.Container(
                expand=True,
                padding=25,
                bgcolor=card_bg,
                border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                content=ft.Column(
                    [
                        ft.Text(
                            "Actividad en Tiempo Real",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Row(
                            [
                                ft.Container(
                                    width=10,
                                    height=10,
                                    bgcolor=ft.Colors.BLUE_400,
                                    border_radius=2,
                                ),
                                ft.Text("Conexiones"),
                                ft.Container(
                                    width=10,
                                    height=10,
                                    bgcolor=ft.Colors.GREEN_400,
                                    border_radius=2,
                                ),
                                ft.Text("QPS"),
                            ],
                            spacing=10,
                        ),
                        ft.Divider(),
                        chart,
                    ]
                ),
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
    )

    # Guardar instancia para reutilizarla
    page.metrics_view_instance = view

    return view