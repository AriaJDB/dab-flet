import flet as ft
from services.metrics_service import *
import time
import asyncio


def metrics_view(page: ft.Page):
    

    # 🧠 --- ESTADO GLOBAL (NO SE REINICIA) ---
    if not hasattr(page, "metrics_state"):
        page.metrics_state = {
            "conexiones_data": [],
            "queries_data": [],
            "last_queries": None,
            "last_time": None
        }

    state = page.metrics_state

    # --- VALORES UI ---
    conexiones_val = ft.Text("0", size=32, weight="bold")
    qps_val = ft.Text("0.0", size=32, weight="bold")
    threads_val = ft.Text("0", size=22, weight="bold")
    bytes_in_val = ft.Text("0", size=22, weight="bold")
    bytes_out_val = ft.Text("0", size=22, weight="bold")
    slow_val = ft.Text("0", size=22, weight="bold")

    # --- CHART ---
    chart = ft.Row(
        height=220,
        spacing=2,
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.END
    )

    def crear_punto(valor, color):
        return ft.Container(
            width=4,
            height=max(2, min(valor * 8, 180)),
            bgcolor=color,
            border_radius=2
        )

    def actualizar_chart():
        chart.controls.clear()

        for i in range(len(state["conexiones_data"])):
            chart.controls.append(
                ft.Column(
                    [
                        crear_punto(state["queries_data"][i], ft.Colors.GREEN_400),
                        crear_punto(state["conexiones_data"][i], ft.Colors.BLUE_400),
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.END
                )
            )

        page.update()

    # 🔁 LOOP PRINCIPAL
    async def loop():
        while True:
            try:
                conexiones = obtener_conexiones()
                queries = obtener_queries()
                threads = obtener_threads_running()
                bytes_in, bytes_out = obtener_bytes()
                slow = obtener_slow_queries()

                now = time.time()

                # 📊 QPS
                if state["last_queries"] is not None:
                    delta_q = queries - state["last_queries"]
                    delta_t = now - state["last_time"]
                    qps = delta_q / delta_t if delta_t > 0 else 0
                else:
                    qps = 0

                # 📈 HISTÓRICO
                state["conexiones_data"].append(conexiones)
                state["queries_data"].append(qps)

                state["conexiones_data"][:] = state["conexiones_data"][-40:]
                state["queries_data"][:] = state["queries_data"][-40:]

                # 🧾 ACTUALIZAR UI
                conexiones_val.value = str(conexiones)
                qps_val.value = str(round(qps, 2))
                threads_val.value = str(threads)
                bytes_in_val.value = str(bytes_in)
                bytes_out_val.value = str(bytes_out)
                slow_val.value = str(slow)

                state["last_queries"] = queries
                state["last_time"] = now

                actualizar_chart()

            except Exception as e:
                print("Error métricas:", e)

            await asyncio.sleep(2)

    # 🚀 INICIAR SOLO UNA VEZ
    if not hasattr(page, "metrics_task_started"):
        page.run_task(loop)
        page.metrics_task_started = True

    # 🎨 THEME
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = ft.Colors.SURFACE_CONTAINER_HIGHEST if is_dark else ft.Colors.WHITE

    # 🧩 COMPONENTE CARD
    def card(titulo, control, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(titulo, size=12),
                control
            ]),
            padding=15,
            border_radius=12,
            bgcolor=card_bg,
            expand=True
        )

    # --- UI FINAL ---
    return ft.Column([

        # HEADER
        ft.Column([
            ft.Text("Métricas del Servidor", size=28, weight="bold"),
            ft.Text("Monitoreo en tiempo real estilo dashboard", color=ft.Colors.BLUE_GREY_400),
        ]),

        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

        # 🔥 KPIs PRINCIPALES
        ft.Row([
            card("Conexiones", conexiones_val, ft.Colors.BLUE_700),
            card("QPS", qps_val, ft.Colors.GREEN_700),
        ], spacing=20),

        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

        # 🧠 MÉTRICAS SECUNDARIAS
        ft.Row([
            card("Threads", threads_val, ft.Colors.ORANGE_700),
            card("Bytes IN", bytes_in_val, ft.Colors.PURPLE_700),
            card("Bytes OUT", bytes_out_val, ft.Colors.CYAN_700),
            card("Slow Queries", slow_val, ft.Colors.RED_700),
        ], spacing=20),

        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

        # 📊 GRÁFICA
        ft.Container(
            content=ft.Column([
                ft.Text("Actividad en tiempo real", weight="bold"),

                ft.Row([
                    ft.Container(width=10, height=10, bgcolor=ft.Colors.BLUE_400),
                    ft.Text("Conexiones"),
                    ft.Container(width=10, height=10, bgcolor=ft.Colors.GREEN_400),
                    ft.Text("QPS"),
                ], spacing=10),

                ft.Divider(),

                chart
            ]),
            padding=25,
            border_radius=15,
            bgcolor=card_bg,
            expand=True
        )

    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)