
import flet as ft
from components.utils import navigation_bar
import requests
from services.api_client import API_BASE_URL
fetch_roles = []
selected_rol = None
selected_rol_id = None

def rol_page(page: ft.Page):
    page.title = "Roles"
    page.padding = 20

    roles_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Editar")),
            ft.DataColumn(ft.Text("Eliminar")),
        ],
        rows=[]
    )
    

    def fetch_roles_data():
        try:
            response = requests.get(f"{API_BASE_URL}/roles")
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            page.snack_bar.content = ft.Text(f"Error al cargar roles: {e}")
            page.snack_bar.open = True
            page.update()
            return []

    def fetch_rol_by_id(rol_id):
        cancel_add() 
        try:
            response = requests.get(f"{API_BASE_URL}/roles/{rol_id}")
            response.raise_for_status()
            return [response.json()]  
        except requests.RequestException as e:
            raise Exception(f"Error al buscar rol por ID: {e}")
    def delete_rol(id):
        try:
            if id is None:
                raise Exception("No se ha seleccionado un rol para eliminar.")
            
            close_delete_dialog()
            response = requests.delete(f"{API_BASE_URL}/roles/{id}")
            if response.status_code == 204:
                page.snack_bar.content = ft.Text("Rol eliminado exitosamente.")
                load_data()
            else:
                raise Exception(f"Error al eliminar rol. Respuesta: {response.status_code}")
        
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al eliminar rol: {ex}")
        
        page.snack_bar.open = True
        page.update()

    def save_changes():
        try:
            global selected_rol
            if not selected_rol:
                raise Exception("No se ha seleccionado un rol para editar.")
            data = {
                "id_rol": selected_rol["id_rol"],
                "descripcion": edit_rol_field.value.strip(),
            }
            data = {key: value for key, value in data.items() if value is not None}

            if not data.get("id_rol"):
                raise Exception("El ID del rol no es válido o está ausente.")

            url = f"{API_BASE_URL}/roles/{data['id_rol']}"
            response = requests.put(url, json=data)

            if response.status_code == 200:
                edit_line.visible = False
                edit_line2.visible = False
                page.snack_bar.content = ft.Text("Rol editado exitosamente.", color="green")
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
        global fetch_roles
        try:
            cancel_add()
            cancel_edit()
            page.snack_bar.content = ft.Text("Cargando roles desde el backend...")
            page.snack_bar.open = True
            page.update()
            fetch_roles = fetch_roles_data()
            if not fetch_roles:
                page.snack_bar.content = ft.Text("No se encontraron roles.")
                page.snack_bar.open = True
                page.update()
                return
            roles_table.rows.clear()

            for rol in fetch_roles:
                if "id_rol" not in rol or "descripcion" not in rol:
                    continue  
                roles_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(rol["id_rol"]))),
                    ft.DataCell(ft.Text(rol["descripcion"])),  
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, rol=rol: edit_rol(rol))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, rol=rol: confirm_delete(rol["id_rol"]))),
                ]))
            page.snack_bar.content = ft.Text("Roles cargados exitosamente.")
            page.snack_bar.open = True
            page.update()

        except Exception as e:
            page.snack_bar.content = ft.Text(f"Error: {str(e)}")
            page.snack_bar.open = True
            page.update()

    def search_by_id(e):
        cancel_add() 
        cancel_edit() 
        rol_id = search_id_field.value
        if not rol_id.isdigit():
            page.snack_bar.content = ft.Text("Por favor, ingresa un ID válido.")
            page.snack_bar.open = True
            page.update()
            search_id_field.value = ""
            return
        try:
            rol = fetch_rol_by_id(rol_id)
            
            roles_table.rows.clear()  

            for r in rol:
                roles_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r["id_rol"]))), 
                    ft.DataCell(ft.Text(r["descripcion"])),  
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, rol=r: edit_rol(r))),  
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, rol=r: confirm_delete(r["id_rol"]))),  
                ]))
            
            page.snack_bar.content = ft.Text(f"Rol con ID {rol_id} cargado exitosamente.")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}")
        page.snack_bar.open = True
        search_id_field.value = ""
        page.update()

    
    def save_new_rol(e):
        try:
            if not add_rol_field.value.strip():
                raise Exception("El nombre y la descripción son campos obligatorios.")
            new_rol_data = {
                "descripcion": add_rol_field.value.strip(), 
        }
            response = requests.post(f"{API_BASE_URL}/roles", json=new_rol_data)
            if response.status_code == 200:
                page.snack_bar.content = ft.Text("Rol agregado exitosamente.", color="green")
                load_data()  
            else:
                raise Exception(f"Error al agregar rol: {response.text}")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}", color="red")
            page.snack_bar.open = True
        finally:
            page.update()

    def show_add_fields(e):
        cancel_edit()
        add_rol_field.value = ""
        add_line.visible = True
        add_line2.visible = True
        page.update()

    def cancel_edit():
        edit_line.visible = False
        edit_line2.visible = False
        page.update()

    def edit_rol(rol):
        cancel_add() 
        global selected_rol
        selected_rol = rol
        edit_rol_field.value = rol["descripcion"]
        edit_line.visible = True
        edit_line2.visible = True
        page.update()

    def confirm_delete(rol_id):
        cancel_add()
        cancel_edit()
        global selected_rol_id
        selected_rol_id = rol_id  
        delete_dialog.open = True
        page.update()

    def close_delete_dialog():
        delete_dialog.open = False
        page.update()

    def cancel_add(e=None):
        add_line.visible = False
        add_line2.visible = False
        add_rol_field.value = ""
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
    add_button = ft.ElevatedButton("Agregar Rol", on_click=show_add_fields)

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
        content=ft.Text("¿Está seguro de que desea eliminar este rol?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: close_delete_dialog()),
            ft.TextButton("Eliminar", on_click=lambda _: delete_rol(selected_rol_id)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    edit_rol_field = ft.TextField(label="Descripción")

    save_button = ft.ElevatedButton("Guardar", on_click=lambda _: save_changes())
    cancel_button = ft.ElevatedButton("Cancelar", on_click=lambda _: cancel_edit())
        
    edit_line.controls = [
        edit_rol_field,
    ]
    edit_line2.controls = [
        save_button,
        cancel_button,  
    ]

    add_rol_field = ft.TextField(label="Descripción")
    save_new_button = ft.ElevatedButton("Agregar", on_click=save_new_rol)
    cancel_new_button = ft.ElevatedButton("Cancelar", on_click=cancel_add)

    add_line = ft.Row(visible=False, controls=[ add_rol_field])
    add_line2 = ft.Row(visible=False, controls=[save_new_button, cancel_new_button])

    roles_table_row = ft.Row(
        controls=[roles_table]
    )
    page_content = ft.Column([navigation_bar(page),ft.Text("Roles", size=30, weight="bold"),
                            top_row,  
                            roles_table_row, 
                            edit_line,
                            edit_line2,  
                            add_line,  
                            add_line2,  
                            delete_dialog 
    ],scroll=ft.ScrollMode.AUTO)
    initialize_snack_bar()
    load_data()
    return page_content