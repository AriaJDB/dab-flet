import flet as ft
from services.metrics_service import *
import time
import asyncio

def metrics_view(page: ft.Page):
    # 🚫 evitar recrear la vista y loop
    if hasattr(page, "metrics_view_instance"):
        return page.metrics_view_instance
    
    conexiones_text = ft.Text("Conexiones: 0", size=18)
    qps_text = ft.Text("QPS: 0", size=18)

    grafica = ft.Row(spacing=5)

    conexiones_data = []
    queries_data = []

    last_queries = None
    last_time = None

    # 📊 actualizar gráfica visual
    def actualizar_grafica():
        grafica.controls.clear()

        for i in range(len(conexiones_data)):
            conexiones = conexiones_data[i]
            qps = queries_data[i]

            grafica.controls.append(
                ft.Column(
                    [
                        ft.Container(
                            width=10,
                            height=conexiones * 5,
                            bgcolor="blue",
                        ),
                        ft.Container(
                            width=10,
                            height=int(qps * 5),
                            bgcolor="red",
                        ),
                    ],
                    spacing=2,
                )
            )

    # 🔄 loop automático
    async def loop():

        nonlocal last_queries, last_time

        while True:
            try:
                conexiones = obtener_conexiones()
                queries = obtener_queries()
                now = time.time()

                conexiones_data.append(conexiones)

                if last_queries is not None:
                    delta_q = queries - last_queries
                    delta_t = now - last_time
                    qps = delta_q / delta_t if delta_t > 0 else 0
                else:
                    qps = 0

                queries_data.append(qps)

                last_queries = queries
                last_time = now

                # limitar datos
                conexiones_data[:] = conexiones_data[-15:]
                queries_data[:] = queries_data[-15:]

                conexiones_text.value = f"Conexiones: {conexiones}"
                qps_text.value = f"QPS: {round(qps, 2)}"

                actualizar_grafica()
                page.update()

            except Exception as e:
                print("ERROR METRICS:", e)

            await asyncio.sleep(2)

    # 🚀 iniciar loop automático
    if not hasattr(page, "metrics_task"):
        page.metrics_task = page.run_task(loop)

    view = ft.Column(
        [
            ft.Text("📊 Métricas de Rendimiento", size=24, weight="bold"),
            conexiones_text,
            qps_text,
            ft.Divider(),
            grafica,
        ]
    )

    # 💾 guardar la vista en memoria
    page.metrics_view_instance = view

    return view