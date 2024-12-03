import flet as ft
import requests
from components.utils import navigation_bar
from services.api_client import API_BASE_URL
fetch_gasolineras = []
selected_gasolinera = None
selected_gasolinera_id = None

def gasolineras_page(page: ft.Page):
    page.title = "Gasolineras"
    page.padding = 20

    gasolineras_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Ubicación")),
            ft.DataColumn(ft.Text("Editar")),
            ft.DataColumn(ft.Text("Eliminar")),
        ],
        rows=[]
    )

    def show_add_fields(e):
        cancel_edit()
        add_name_field.value = ""
        add_location_field.value = ""
        add_line.visible = True
        add_line2.visible = True
        page.update()

    def fetch_gasolineras_data():
        try:
            response = requests.get(f"{API_BASE_URL}/gasolineras")
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            page.snack_bar.content = ft.Text(f"Error al cargar gasolineras: {e}")
            page.snack_bar.open = True
            page.update()
            return []

    def fetch_gasolinera_by_id(gasolinera_id):
        try:
            response = requests.get(f"{API_BASE_URL}/gasolineras/{gasolinera_id}")
            response.raise_for_status()
            return [response.json()]  
        except requests.RequestException as e:
            raise Exception(f"Error al buscar gasolinera por ID: {e}")

    def delete_gasolinera(id):
        try:            
            if id is None:
                raise Exception("No se ha seleccionado una gasolinera para eliminar.")
            
            close_delete_dialog() 
            response = requests.delete(f"{API_BASE_URL}/gasolineras/{id}")
            if response.status_code == 204: 
                page.snack_bar.content = ft.Text("Gasolinera eliminada exitosamente.")
                load_data()
            else:
                raise Exception(f"Error al eliminar gasolinera. Respuesta: {response.status_code}")
        
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al eliminar gasolinera: {ex}")
        
        page.snack_bar.open = True
        page.update()

    def save_changes():
        try:
            global selected_gasolinera
            if not selected_gasolinera:
                raise Exception("No se ha seleccionado una gasolinera para editar.")
            data = {
                "id_gasolinera": selected_gasolinera.get("id_gasolinera"),
                "nombre": name_field.value.strip() if name_field.value else None,
                "direccion": location_field.value.strip() if location_field.value else None,
            }
            data = {key: value for key, value in data.items() if value is not None}
            if not data.get("id_gasolinera"):
                raise Exception("El ID de la gasolinera no es válido o está ausente.")

            url = f"{API_BASE_URL}/gasolineras/{data['id_gasolinera']}"
            response = requests.put(url, json=data)
            if response.status_code == 200:
                edit_line.visible = False
                edit_line2.visible = False
                page.snack_bar.content = ft.Text("Gasolinera editada exitosamente.", color="green")
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
        global fetch_gasolineras
        try:
            cancel_add()
            cancel_edit()
            page.snack_bar.content = ft.Text("Cargando gasolineras desde el backend...")
            page.snack_bar.open = True
            page.update()
            fetch_gasolineras = fetch_gasolineras_data()
            if not fetch_gasolineras:
                page.snack_bar.content = ft.Text("No se encontraron gasolineras.")
                page.snack_bar.open = True
                page.update()
                return
            gasolineras_table.rows.clear()

            for gasolinera in fetch_gasolineras:
                if "id_gasolinera" not in gasolinera or "nombre" not in gasolinera or "direccion" not in gasolinera:
                    continue  
                gasolineras_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(gasolinera["id_gasolinera"]))),
                    ft.DataCell(ft.Text(gasolinera["nombre"])),
                    ft.DataCell(ft.Text(gasolinera["direccion"])),  
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, gasolinera=gasolinera: edit_gasolinera(gasolinera))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, gasolinera=gasolinera: confirm_delete(gasolinera["id_gasolinera"]))),
                ]))

            page.snack_bar.content = ft.Text("Gasolineras cargadas exitosamente.")
            page.snack_bar.open = True
            page.update()

        except Exception as e:
            page.snack_bar.content = ft.Text(f"Error: {str(e)}")
            page.snack_bar.open = True
            page.update()

    def search_by_id(e):
        cancel_add() 
        cancel_edit() 
        gasolinera_id = search_id_field.value
        if not gasolinera_id.isdigit():
            page.snack_bar.content = ft.Text("Por favor, ingresa un ID válido.")
            page.snack_bar.open = True
            page.update()
            search_id_field.value = ""
            return
        try:
            gasolinera = fetch_gasolinera_by_id(gasolinera_id)
            
            gasolineras_table.rows.clear()  

            for g in gasolinera:
                gasolineras_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(g["id_gasolinera"]))), 
                    ft.DataCell(ft.Text(g["nombre"])),  
                    ft.DataCell(ft.Text(g["direccion"])),  
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, gasolinera=g: edit_gasolinera(g))),  
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, gasolinera=g: confirm_delete(g["id_gasolinera"]))),  
                ]))
            
            page.snack_bar.content = ft.Text(f"Gasolinera con ID {gasolinera_id} cargada exitosamente.")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}")
        page.snack_bar.open = True
        search_id_field.value = ""
        page.update()

    def cancel_edit():
        edit_line.visible = False
        edit_line2.visible = False
        page.update()

    def edit_gasolinera(gasolinera):
        cancel_add() 
        global selected_gasolinera
        selected_gasolinera = gasolinera
        name_field.value = gasolinera["nombre"]
        location_field.value = gasolinera["direccion"] 
        
        edit_line.visible = True
        edit_line2.visible = True
        page.update()

    def confirm_delete(gasolinera_id):
        cancel_add()
        cancel_edit() 
        global selected_gasolinera_id
        selected_gasolinera_id = gasolinera_id  
        delete_dialog.open = True
        page.update()

    def close_delete_dialog():
        delete_dialog.open = False
        page.update()
    def save_new_gasolinera(e):
        try:
            if not add_name_field.value.strip() or not add_location_field.value.strip():
                raise Exception("El nombre y la ubicación son campos obligatorios.")
            
            new_gasolinera_data = {
                "nombre": add_name_field.value.strip(),
                "direccion": add_location_field.value.strip(), 
           }
            response = requests.post(f"{API_BASE_URL}/gasolineras", json=new_gasolinera_data)
            if response.status_code == 200:
                page.snack_bar.content = ft.Text("Gasolinera agregada exitosamente.", color="green")
                load_data()  
            else:
                raise Exception(f"Error al agregar gasolinera: {response.text}")

        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}", color="red")
            page.snack_bar.open = True
        finally:
            page.update()
    def cancel_add(e=None):
        add_line.visible = False
        add_line2.visible = False
        add_name_field.value = ""
        add_location_field.value = ""
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
    add_button = ft.ElevatedButton("Agregar Gasolinera", on_click=show_add_fields)

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
        content=ft.Text("¿Está seguro de que desea eliminar esta gasolinera?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: close_delete_dialog()),
            ft.TextButton("Eliminar", on_click=lambda _: delete_gasolinera(selected_gasolinera_id)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    name_field = ft.TextField(label="Nombre")
    location_field = ft.TextField(label="Ubicación")

    save_button = ft.ElevatedButton("Guardar", on_click=lambda _: save_changes())
    cancel_button = ft.ElevatedButton("Cancelar", on_click=lambda _: cancel_edit())
    
    edit_line.controls = [
        name_field,
        location_field,
    ]
    edit_line2.controls = [
        save_button,
        cancel_button,  
    ]

    add_name_field = ft.TextField(label="Nombre")
    add_location_field = ft.TextField(label="Ubicación")
    save_new_button = ft.ElevatedButton("Agregar", on_click=save_new_gasolinera)
    cancel_new_button = ft.ElevatedButton("Cancelar", on_click=cancel_add)

    add_line = ft.Row(visible=False, controls=[add_name_field, add_location_field])
    add_line2 = ft.Row(visible=False, controls=[save_new_button, cancel_new_button])

    gasolineras_table_row = ft.Row(
        controls=[gasolineras_table]
    )
    
    page_content = ft.Column([navigation_bar(page),
                                ft.Text("Gasolineras", size=30, weight="bold"),
                                top_row,  
                                gasolineras_table_row, 
                                edit_line,
                                edit_line2,  
                                add_line,  
                                add_line2,  
                                delete_dialog 
    ],scroll=ft.ScrollMode.AUTO)
    initialize_snack_bar()
    load_data()
    return page_content


