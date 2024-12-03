
import flet as ft
from components.utils import navigation_bar
import requests
from services.api_client import API_BASE_URL

def log_page(page: ft.Page):
    log_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("DESCRIPCIÓN", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("FECHA", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("USERNAME", style=ft.TextStyle(size=12))),
        ],
        rows=[],
        divider_thickness=0.5,
        heading_row_height=35,
    )

    def initialize_snack_bar():
        if not hasattr(page, 'snack_bar') or page.snack_bar is None:
            page.snack_bar = ft.SnackBar(ft.Text("Mensaje predeterminado"))

    def fetch_log_data():
        try:
            response = requests.get(f"{API_BASE_URL}/logs2")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            page.snack_bar.content = ft.Text(f"Error al cargar logs: {e}")
            page.snack_bar.open = True
            page.update()
            return []

    def fetch_log_by_id(log_id):
        try:
            response = requests.get(f"{API_BASE_URL}/logs2/{log_id}")
            response.raise_for_status()
            return [response.json()]
        except requests.RequestException as e:
            raise Exception(f"Error al buscar log por ID: {e}")

    def load_data():
        try:
            logs = fetch_log_data()
            log_table.rows.clear()
            for log in logs:
                log_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(log.get("id_log", "")))),
                    ft.DataCell(ft.Text(str(log.get("descripcion", "")))),
                    ft.DataCell(ft.Text(str(log.get("fecha", "")))),
                    ft.DataCell(ft.Text(str(log.get("username", "")))),
                ]))

            page.snack_bar.content = ft.Text("Logs cargados exitosamente.")
        except Exception as e:
            page.snack_bar.content = ft.Text(f"Error al cargar logs: {e}")
        page.snack_bar.open = True
        page.update()

    def search_by_id(e):
        log_id = search_id_field.value
        if not log_id.isdigit():
            page.snack_bar.content = ft.Text("Por favor, ingresa un ID válido.")
            page.snack_bar.open = True
            page.update()
            search_id_field.value = ""
            return
        try:
            log = fetch_log_by_id(log_id)
            log_table.rows.clear()

            for l in log:
                log_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(l["id_log"]))),
                    ft.DataCell(ft.Text(l["descripcion"])),
                    ft.DataCell(ft.Text(str(l["fecha"]))),
                    ft.DataCell(ft.Text(str(l["username"]))),
                ]))

            page.snack_bar.content = ft.Text(f"Log con ID {log_id} cargado exitosamente.")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}")
        page.snack_bar.open = True
        search_id_field.value = ""
        page.update()
    search_id_field = ft.TextField(label="Buscar por ID", width=200)
    search_id_button = ft.IconButton(
        icon=ft.icons.SEARCH,
        on_click=search_by_id,
        tooltip="Buscar por ID"
    )
    reload_button = ft.ElevatedButton("Cargar Todos", on_click=lambda _: load_data())
    top_row = ft.Row(
        controls=[search_id_field, search_id_button, reload_button],
        alignment=ft.MainAxisAlignment.START
    )
    page_content = ft.Column([navigation_bar(page),ft.Text("Logs", size=30, weight="bold"),top_row, log_table],scroll=ft.ScrollMode.AUTO)
    
    initialize_snack_bar()
    load_data()  # Cargar datos al inicio
    return page_content
