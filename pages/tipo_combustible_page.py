
import flet as ft
from components.utils import navigation_bar
import requests
from services.api_client import API_BASE_URL
fetch_tipos_combustible = []
selected_tipo_combustible = None
selected_tipo_combustible_id = None

def tipo_combustible_page(page: ft.Page):
    page.title = "Tipos de Combustible"
    page.padding = 20

    tipos_combustible_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Editar")),
            ft.DataColumn(ft.Text("Eliminar")),
        ],
        rows=[]
    )
    

    def fetch_tipos_combustible_data():
        try:
            response = requests.get(f"{API_BASE_URL}/tipos_combustible")
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            page.snack_bar.content = ft.Text(f"Error al cargar tipos de combustible: {e}")
            page.snack_bar.open = True
            page.update()
            return []

    def fetch_tipo_combustible_by_id(tipo_combustible_id):
        cancel_add() 
        try:
            response = requests.get(f"{API_BASE_URL}/tipos_combustible/{tipo_combustible_id}")
            response.raise_for_status()
            return [response.json()]  
        except requests.RequestException as e:
            raise Exception(f"Error al buscar tipo de combustible por ID: {e}")
    
    def delete_tipo_combustible(id):
        try:
            if id is None:
                raise Exception("No se ha seleccionado un tipo de combustible para eliminar.")
            
            close_delete_dialog()
            response = requests.delete(f"{API_BASE_URL}/tipos_combustible/{id}")
            if response.status_code == 204:
                page.snack_bar.content = ft.Text("Tipo de combustible eliminado exitosamente.")
                load_data()
            else:
                raise Exception(f"Error al eliminar tipo de combustible. Respuesta: {response.status_code}")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al eliminar tipo de combustible: {ex}")
        page.snack_bar.open = True
        page.update()

    def save_changes():
        try:
            global selected_tipo_combustible
            if not selected_tipo_combustible:
                raise Exception("No se ha seleccionado un tipo de combustible para editar.")
            data = {
                "id_tipo_combustible": selected_tipo_combustible["id_tipo_combustible"],
                "descripcion": edit_tipo_combustible_field.value.strip(),
            }
            data = {key: value for key, value in data.items() if value is not None}
            if not data.get("id_tipo_combustible"):
                raise Exception("El ID del tipo de combustible no es válido o está ausente.")
            url = f"{API_BASE_URL}/tipos_combustible/{data['id_tipo_combustible']}"
            response = requests.put(url, json=data)
            if response.status_code == 200:
                edit_line.visible = False
                edit_line2.visible = False
                page.snack_bar.content = ft.Text("Tipo de combustible editado exitosamente.", color="green")
                load_data()
            else:
                raise Exception(f"Error en la respuesta del servidor: {response.status_code} - {response.text}")

        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al guardar cambios: {ex}", color="red")
            page.snack_bar.open = True

        finally:
            page.update()


    def initialize_snack_bar():
        if not hasattr(page, 'snack_bar') or page.snack_bar is None:
            page.snack_bar = ft.SnackBar(ft.Text("Mensaje predeterminado"))
    def load_data(e=None):
        global fetch_tipos_combustible
        try:
            cancel_edit()
            cancel_add()
            page.snack_bar.content = ft.Text("Cargando tipos de combustible desde el backend...")
            page.snack_bar.open = True
            page.update()
            fetch_tipos_combustible = fetch_tipos_combustible_data()
            if not fetch_tipos_combustible:
                page.snack_bar.content = ft.Text("No se encontraron tipos de combustible.")
                page.snack_bar.open = True
                page.update()
                return
            tipos_combustible_table.rows.clear()

            for tipo_combustible in fetch_tipos_combustible:
                if "id_tipo_combustible" not in tipo_combustible or "descripcion" not in tipo_combustible:
                    continue  
                tipos_combustible_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(tipo_combustible["id_tipo_combustible"]))),
                    ft.DataCell(ft.Text(tipo_combustible["descripcion"])),  
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, tipo_combustible=tipo_combustible: edit_tipo_combustible(tipo_combustible))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, tipo_combustible=tipo_combustible: confirm_delete(tipo_combustible["id_tipo_combustible"]))),
                ]))

            page.snack_bar.content = ft.Text("Tipos de combustible cargados exitosamente.")
            page.snack_bar.open = True
            page.update()

        except Exception as e:
            page.snack_bar.content = ft.Text(f"Error: {str(e)}")
            page.snack_bar.open = True
            page.update()

    def search_by_id(e):
        cancel_add() 
        cancel_edit() 
        tipo_combustible_id = search_id_field.value
        if not tipo_combustible_id.isdigit():
            page.snack_bar.content = ft.Text("Por favor, ingresa un ID válido.")
            page.snack_bar.open = True
            page.update()
            search_id_field.value = ""
            return
        try:
            tipo_combustible = fetch_tipo_combustible_by_id(tipo_combustible_id)
            
            tipos_combustible_table.rows.clear()  

            for t in tipo_combustible:
                tipos_combustible_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(t["id_tipo_combustible"]))), 
                    ft.DataCell(ft.Text(t["descripcion"])),  
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, tipo_combustible=t: edit_tipo_combustible(t))),  
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, tipo_combustible=t: confirm_delete(t["id_tipo_combustible"]))),  
                ]))
            
            page.snack_bar.content = ft.Text(f"Tipo de combustible con ID {tipo_combustible_id} cargado exitosamente.")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}")
        page.snack_bar.open = True
        search_id_field.value = ""
        page.update()

    def save_new_tipo_combustible(e):
        try:
            if not add_tipo_combustible_field.value.strip():
                raise Exception("la descripción es obligatorio.")
            
            new_tipo_combustible_data = {
                "descripcion": add_tipo_combustible_field.value.strip(), 
            }
            response = requests.post(f"{API_BASE_URL}/tipos_combustible", json=new_tipo_combustible_data)
            if response.status_code == 200:
                page.snack_bar.content = ft.Text("Tipo de combustible agregado exitosamente.", color="green")
                cancel_add() 
                load_data()  
            else:
                raise Exception(f"Error al agregar tipo de combustible: {response.text}")

        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}", color="red")
            page.snack_bar.open = True
        finally:
            page.update()
    def show_add_fields(e):
        cancel_edit()
        add_tipo_combustible_field.value = ""
        add_line.visible = True
        add_line2.visible = True
        page.update()

    def cancel_edit():
        edit_line.visible = False
        edit_line2.visible = False
        page.update()

    def edit_tipo_combustible(tipo_combustible):
        cancel_add() 
        global selected_tipo_combustible
        selected_tipo_combustible = tipo_combustible
        edit_tipo_combustible_field.value = tipo_combustible["descripcion"]
        
        edit_line.visible = True
        edit_line2.visible = True
        page.update()

    def confirm_delete(tipo_combustible_id):
        cancel_add() 
        cancel_edit()
        global selected_tipo_combustible_id
        selected_tipo_combustible_id = tipo_combustible_id  
        delete_dialog.open = True
        page.update()

    def close_delete_dialog():
        delete_dialog.open = False
        page.update()

    def cancel_add(e=None):
        add_line.visible = False
        add_line2.visible = False
        add_tipo_combustible_field.value = ""
        page.update()
    edit_line = ft.Row(visible=False, controls=[])
    edit_line2 = ft.Row(visible=False, controls=[])

    search_id_field = ft.TextField(label="Buscar por ID", width=200)
    search_id_button = ft.IconButton(
        icon=ft.icons.SEARCH,
        on_click=search_by_id,
        tooltip="Buscar por ID"
    )

    reload_button = ft.ElevatedButton("Cargar", on_click=load_data)
    add_button = ft.ElevatedButton("Agregar Tipo de Combustible", on_click=show_add_fields)

    top_row = ft.Row(
        controls=[
            search_id_field,
            search_id_button,
            reload_button,
            add_button, 
        ]
    )

    delete_dialog = ft.AlertDialog(
        title=ft.Text("Confirmar eliminación"),
        content=ft.Text("¿Está seguro de que desea eliminar este tipo de combustible?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: close_delete_dialog()),
            ft.TextButton("Eliminar", on_click=lambda _: delete_tipo_combustible(selected_tipo_combustible_id)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    edit_tipo_combustible_field = ft.TextField(label="Descripción")

    save_button = ft.ElevatedButton("Guardar", on_click=lambda _: save_changes())
    cancel_button = ft.ElevatedButton("Cancelar", on_click=lambda _: cancel_edit())

    edit_line.controls = [
        edit_tipo_combustible_field,
    ]
    edit_line2.controls = [
        save_button,
        cancel_button,  
    ]

    add_tipo_combustible_field = ft.TextField(label="Descripción")
    save_new_button = ft.ElevatedButton("Agregar", on_click=save_new_tipo_combustible)
    cancel_new_button = ft.ElevatedButton("Cancelar", on_click=cancel_add)

    add_line = ft.Row(visible=False, controls=[add_tipo_combustible_field])
    add_line2 = ft.Row(visible=False, controls=[save_new_button, cancel_new_button])

    tipos_combustible_table_row = ft.Row(
        controls=[tipos_combustible_table]
    )

    page_content = ft.Column([navigation_bar(page),ft.Text("Tipo de Combustible", size=30, weight="bold"),
        top_row,  
        tipos_combustible_table_row, 
        edit_line,
        edit_line2,  
        add_line,  
        add_line2,  
        delete_dialog 
    ],scroll=ft.ScrollMode.AUTO)
    initialize_snack_bar()
    load_data()
    return page_content