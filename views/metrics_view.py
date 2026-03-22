import flet as ft
from services.metrics_service import *
import time
import asyncio

def metrics_view(page: ft.Page):
    # 🚫 Singleton para evitar duplicar hilos
    if hasattr(page, "metrics_view_instance"):
        return page.metrics_view_instance
    
    # --- Controles de Texto (KPIs) ---
    conexiones_val = ft.Text("0", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
    qps_val = ft.Text("0.0", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)

    # --- Contenedor de Gráfica ---
    # Usaremos un Row con alineación inferior para que las barras crezcan hacia arriba
    grafica_container = ft.Row(
        spacing=8, 
        alignment=ft.MainAxisAlignment.START, 
        vertical_alignment=ft.CrossAxisAlignment.END,
        height=200
    )

    conexiones_data = []
    queries_data = []
    last_queries = None
    last_time = None

    def crear_barra(valor, color, tooltip):
        # Normalizamos la altura (ej. valor * 10) para que sea visible
        altura = max(2, min(valor * 10, 150)) 
        return ft.Container(
            width=12,
            height=altura,
            bgcolor=color,
            border_radius=ft.BorderRadius(5, 5, 0, 0),
            tooltip=f"{tooltip}: {valor}"
        )

    def actualizar_interfaz():
        grafica_container.controls.clear()
        
        for i in range(len(conexiones_data)):
            c_val = conexiones_data[i]
            q_val = queries_data[i]

            grafica_container.controls.append(
                ft.Column([
                    crear_barra(q_val, ft.Colors.GREEN_400, "QPS"),
                    crear_barra(c_val, ft.Colors.BLUE_400, "Conexiones"),
                ], spacing=2, alignment=ft.MainAxisAlignment.END)
            )
        page.update()

    async def loop():
        nonlocal last_queries, last_time
        while True:
            try:
                # Consultar servicios
                conexiones = obtener_conexiones()
                queries = obtener_queries()
                now = time.time()

                # Lógica de cálculo QPS
                if last_queries is not None:
                    delta_q = queries - last_queries
                    delta_t = now - last_time
                    qps = delta_q / delta_t if delta_t > 0 else 0
                else:
                    qps = 0

                # Actualizar listas de datos (Historial de 20 puntos)
                conexiones_data.append(conexiones)
                queries_data.append(qps)
                conexiones_data[:] = conexiones_data[-20:]
                queries_data[:] = queries_data[-20:]

                # Actualizar valores de los textos
                conexiones_val.value = str(conexiones)
                qps_val.value = str(round(qps, 2))

                last_queries = queries
                last_time = now

                actualizar_interfaz()

            except Exception as e:
                print(f"Error en Métricas: {e}")
            
            await asyncio.sleep(2)

    # Iniciar la tarea asíncrona usando el nuevo método de Flet
    if not hasattr(page, "metrics_task_started"):
        page.run_task(loop)
        page.metrics_task_started = True

    # --- DISEÑO DEL DASHBOARD ---
    view = ft.Column([
        # Título
        ft.Row([
            ft.Column([
                ft.Text("Estado del Servidor", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Monitoreo en tiempo real de tráfico y sesiones", color=ft.Colors.BLUE_GREY_400),
            ])
        ]),

        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

        # Fila de Tarjetas de Resumen (KPIs)
        ft.Row([
            # Card Conexiones
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.LANGUAGE_ROUNDED, color=ft.Colors.BLUE_700),
                    ft.Text("Conexiones Activas", size=14, color=ft.Colors.BLUE_GREY_500),
                    conexiones_val
                ], spacing=5),
                expand=True, padding=20, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE, border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
            ),
            # Card QPS
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SPEED_ROUNDED, color=ft.Colors.GREEN_700),
                    ft.Text("Queries por Segundo (QPS)", size=14, color=ft.Colors.BLUE_GREY_500),
                    qps_val
                ], spacing=5),
                expand=True, padding=20, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE, border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
            ),
        ], spacing=20),

        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

        # Card de la Gráfica
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Historial de Actividad", weight=ft.FontWeight.BOLD, size=18),
                    ft.Row([
                        ft.Container(width=10, height=10, bgcolor=ft.Colors.BLUE_400, border_radius=2),
                        ft.Text("Conexiones", size=12),
                        ft.Container(width=10, height=10, bgcolor=ft.Colors.GREEN_400, border_radius=2),
                        ft.Text("QPS", size=12),
                    ], spacing=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Container(content=grafica_container, padding=ft.Padding.only(top=20))
            ]),
            padding=25,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
            expand=True
        )
    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)

    page.metrics_view_instance = view
    return view