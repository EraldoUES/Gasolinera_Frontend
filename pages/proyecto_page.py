import flet as ft
import requests
from components.utils import navigation_bar
from services.api_client import API_BASE_URL
fetch_proyectos = []
selected_proyecto = None
selected_proyecto_id = None

def proyecto_page(page: ft.Page):
    page.title = "Proyectos"
    page.padding = 20

    proyectos_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Ubicación")),
            ft.DataColumn(ft.Text("Activo")),
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

    def fetch_proyectos_data():
        try:
            response = requests.get(f"{API_BASE_URL}/proyectos")
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            page.snack_bar.content = ft.Text(f"Error al cargar proyectos: {e}")
            page.snack_bar.open = True
            page.update()
            return []

    def fetch_proyecto_by_id(proyecto_id):
        try:
            response = requests.get(f"{API_BASE_URL}/proyectos/{proyecto_id}")
            response.raise_for_status()
            return [response.json()]  
        except requests.RequestException as e:
            raise Exception(f"Error al buscar proyecto por ID: {e}")

    def delete_proyecto(id):
        try:            
            if id is None:
                raise Exception("No se ha seleccionado una proyecto para eliminar.")
            close_delete_dialog() 
            response = requests.delete(f"{API_BASE_URL}/proyectos/{id}")
            if response.status_code == 204: 
                page.snack_bar.content = ft.Text("Proyecto eliminada exitosamente.")
                load_data()
            else:
                raise Exception(f"Error al eliminar proyecto. Respuesta: {response.status_code}")
        
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al eliminar proyecto: {ex}")
        
        page.snack_bar.open = True
        page.update()

    def save_changes():
        try:
            global selected_proyecto
            if not selected_proyecto:
                raise Exception("No se ha seleccionado un proyecto para editar.")
            data = {
                "id_proyecto": selected_proyecto.get("id_proyecto"),
                "nombre": name_field.value.strip() if name_field.value else None,
                "direccion": location_field.value.strip() if location_field.value else None,
                "activo": edit_active_dropdown.value=="Activo",
            }
            data = {key: value for key, value in data.items() if value is not None}

            if not data.get("id_proyecto"):
                raise Exception("El ID del proyecto no es válido o está ausente.")
            url = f"{API_BASE_URL}/proyectos/{data['id_proyecto']}"
            response = requests.put(url, json=data)

            if response.status_code == 200:
                # Ocultar las líneas de edición
                edit_line.visible = False
                edit_line2.visible = False
                page.snack_bar.content = ft.Text("Proyecto editado exitosamente.", color="green")
                load_data()  # Recargar la lista de proyectos
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
        global fetch_proyectos
        try:
            cancel_add()
            cancel_edit() 
            page.snack_bar.content = ft.Text("Cargando proyectos desde el backend...")
            page.snack_bar.open = True
            page.update()

            fetch_proyectos = fetch_proyectos_data()

            if not fetch_proyectos:
                page.snack_bar.content = ft.Text("No se encontraron proyectos.")
                page.snack_bar.open = True
                page.update()
                return
            proyectos_table.rows.clear()

            for proyecto in fetch_proyectos:
                if "id_proyecto" not in proyecto or "nombre" not in proyecto or "direccion" not in proyecto:
                    continue  
                proyectos_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(proyecto["id_proyecto"]))),
                    ft.DataCell(ft.Text(proyecto["nombre"])),
                    ft.DataCell(ft.Text(proyecto["direccion"])), 
                    ft.DataCell(ft.Text(proyecto["activo"])),  
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, proyecto=proyecto: edit_proyecto(proyecto))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, proyecto=proyecto: confirm_delete(proyecto["id_proyecto"]))),
                ]))

            page.snack_bar.content = ft.Text("Proyectos cargadas exitosamente.")
            page.snack_bar.open = True
            page.update()

        except Exception as e:
            page.snack_bar.content = ft.Text(f"Error: {str(e)}")
            page.snack_bar.open = True
            page.update()


    def search_by_id(e):
        cancel_add()
        cancel_edit()
        proyecto_id = search_id_field.value
        if not proyecto_id.isdigit():
            page.snack_bar.content = ft.Text("Por favor, ingresa un ID válido.")
            page.snack_bar.open = True
            page.update()
            search_id_field.value = ""
            return
        try:
            proyecto = fetch_proyecto_by_id(proyecto_id)
            
            proyectos_table.rows.clear()  

            for g in proyecto:
                proyectos_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(g["id_proyecto"]))), 
                    ft.DataCell(ft.Text(g["nombre"])),  
                    ft.DataCell(ft.Text(g["direccion"])),  
                    ft.DataCell(ft.Text(g["activo"])),  
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, proyecto=g: edit_proyecto(g))),  
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, proyecto=g: confirm_delete(g["id_proyecto"]))),  
                ]))
            
            page.snack_bar.content = ft.Text(f"Proyecto con ID {proyecto_id} cargada exitosamente.")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}")
        page.snack_bar.open = True
        search_id_field.value = ""
        page.update()

    def cancel_edit():
        edit_line.visible = False
        edit_line2.visible = False
        page.update()

    def edit_proyecto(proyecto):
        cancel_add() 
        global selected_proyecto
        selected_proyecto = proyecto
        name_field.value = proyecto["nombre"]
        location_field.value = proyecto["direccion"]
        edit_active_dropdown.value = "true" if proyecto["activo"] else "false"
        edit_line.visible = True
        edit_line2.visible = True
        page.update()
    def confirm_delete(proyecto_id):
        cancel_add()
        cancel_edit()
        global selected_proyecto_id
        selected_proyecto_id = proyecto_id  
        delete_dialog.open = True
        page.update()

    def close_delete_dialog():
        delete_dialog.open = False
        page.update()
    def save_new_proyecto(e):
        try:
            if not add_name_field.value.strip() or not add_location_field.value.strip():
                raise Exception("El nombre y la ubicación son campos obligatorios.")
            
            new_proyecto_data = {
                "nombre": add_name_field.value.strip(),
                "direccion": add_location_field.value.strip(), 
                "activo": add_active_dropdown.value == "Activo",
           }
            response = requests.post(f"{API_BASE_URL}/proyectos", json=new_proyecto_data)
            if response.status_code == 200:
                page.snack_bar.content = ft.Text("Proyecto agregado exitosamente.", color="green")
                load_data()
            else:
                raise Exception(f"Error al agregar proyecto: {response.text}")

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
    add_button = ft.ElevatedButton("Agregar Proyecto", on_click=show_add_fields)

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
        content=ft.Text("¿Está seguro de que desea eliminar esta proyecto?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: close_delete_dialog()),
            ft.TextButton("Eliminar", on_click=lambda _: delete_proyecto(selected_proyecto_id)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    name_field = ft.TextField(label="Nombre")
    location_field = ft.TextField(label="Ubicación")
    edit_active_dropdown = ft.Dropdown(
        label="Estado",
        options=[
            ft.dropdown.Option("Activo"),
            ft.dropdown.Option("Inactivo")
        ],
        value="Activo" 
    )

    save_button = ft.ElevatedButton("Guardar", on_click=lambda _: save_changes())
    cancel_button = ft.ElevatedButton("Cancelar", on_click=lambda _: cancel_edit())
    
    edit_line.controls = [
        name_field,
        location_field,
        edit_active_dropdown,
    ]
    edit_line2.controls = [
        save_button,
        cancel_button,  
    ]
    add_name_field = ft.TextField(label="Nombre")
    add_location_field = ft.TextField(label="Dirección")
    add_active_dropdown = ft.Dropdown(
        label="Estado",
        options=[
            ft.dropdown.Option("Activo"),
            ft.dropdown.Option("Inactivo")
        ],
        value="Activo"  # Establece "Activo" como valor predeterminado
    )


    add_line = ft.Row(visible=False, controls=[add_name_field, add_location_field, add_active_dropdown])
    add_line2 = ft.Row(visible=False, controls=[
        ft.ElevatedButton("Agregar", on_click=save_new_proyecto),
        ft.ElevatedButton("Cancelar", on_click=cancel_add)
    ])

    proyectos_table_row = ft.Row(
        controls=[proyectos_table]
    )

    initialize_snack_bar()
    load_data()    
    page_content = ft.Column([navigation_bar(page),ft.Text("Proyectos", size=30, weight="bold"),
                                top_row,
                                proyectos_table_row, 
                                edit_line,
                                edit_line2,  
                                add_line,  
                                add_line2,  
                                delete_dialog 
    ],scroll=ft.ScrollMode.AUTO)
    return page_content