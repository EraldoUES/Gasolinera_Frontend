import flet as ft
import requests
from components.utils import navigation_bar
from services.api_client import API_BASE_URL
roles_global=[]
selected_user = None
selected_user_id = None
def usuarios_page(page: ft.Page):
    page.title = "Usuarios"
    page.padding = 20
    def init_snack_bar():
        page.snack_bar = ft.SnackBar(content=ft.Text(""), open=False)
    usuarios_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Apellido")),
            ft.DataColumn(ft.Text("Username")),
            ft.DataColumn(ft.Text("Rol")),
            ft.DataColumn(ft.Text("Activo")),
            ft.DataColumn(ft.Text("Editar")),
            ft.DataColumn(ft.Text("Eliminar")),
        ],
        rows=[]
    )

    def fetch_roles():
        try:
            response = requests.get(f"{API_BASE_URL}/roles")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            page.snack_bar.content = ft.Text(f"Error al cargar roles: {e}")
            page.snack_bar.open = True
            page.update()
            return []

    def fetch_users():
        try:
            response = requests.get(f"{API_BASE_URL}/users2")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error al obtener usuarios: {e}")

    def fetch_user_by_id(user_id):
        try:
            response = requests.get(f"{API_BASE_URL}/users2.id/{user_id}")
            response.raise_for_status()
            return [response.json()]
        except requests.RequestException as e:
            raise Exception(f"Error al buscar usuario por ID: {e}")

    def fetch_user_by_username(username):
        try:
            response = requests.get(f"{API_BASE_URL}/users2.name/{username}")
            response.raise_for_status()
            return [response.json()]
        except requests.RequestException as e:
            raise Exception(f"Error al buscar usuario por username: {e}")

    def delete_user(id):
        try:
            if id is None:
                raise Exception("No se ha seleccionado un usuario para eliminar.")

            close_delete_dialog()
            response = requests.delete(f"{API_BASE_URL}/users2/{id}")
            if response.status_code == 204:
                page.snack_bar.content = ft.Text("Usuario eliminado exitosamente.")
                load_data()
            else:
                raise Exception(f"Error al eliminar usuario. Respuesta: {response.status_code}")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al eliminar usuario: {ex}")
        page.snack_bar.open = True
        page.update()

    def save_changes():
        try:
            global selected_user
            if selected_user is None:
                raise Exception("No se ha seleccionado un usuario para editar.")

            if not roles_global:
                raise Exception("Los roles no se han cargado correctamente.")

            selected_role = None
            for role in roles_global:
                if role["descripcion"] == role_dropdown.value:
                    selected_role = role
                    break

            if selected_role is None:
                raise Exception("No se ha seleccionado un rol válido.")

            data = {
                "id_usr": selected_user["id_usr"],
                "nombre": name_field.value if name_field.value else None,
                "apellido": last_name_field.value if last_name_field.value else None,
                "username": username_field.value if username_field.value else None,
                "id_rol": selected_role["id_rol"] if selected_role else None,
                "activo": "Activo" == active_dropdown.value,
                "contraseña": password_field.value if password_field.value else None
            }

            data = {key: value for key, value in data.items() if value is not None}
            if selected_user.get("id_usr") is None:
                raise Exception("ID del usuario no válido.")

            response = requests.put(f"{API_BASE_URL}/users2/{selected_user['id_usr']}", json=data)
            if response.status_code == 200:
                page.snack_bar.content = ft.Text("Usuario editado exitosamente.")
                load_data()
            else:
                raise Exception(f"Error en la respuesta del servidor: {response.status_code}")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al guardar cambios: {ex}")
            page.snack_bar.open = True
        page.update()

    def load_data(e=None):
        try:
            cancel_edit()
            cancel_add()
            users = fetch_users()
            usuarios_table.rows.clear()
            for user in users:
                usuarios_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(user["id_usr"]))),
                    ft.DataCell(ft.Text(user["nombre"])),
                    ft.DataCell(ft.Text(user["apellido"])),
                    ft.DataCell(ft.Text(user["username"])),
                    ft.DataCell(ft.Text(user["rol"])),
                    ft.DataCell(ft.Text("Activo" if user["activo"] else "Inactivo")),
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, user=user: edit_user(user))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, user=user: confirm_delete(user["id_usr"])))
                ]))
            page.update()
        except Exception as e:
            page.snack_bar.content = ft.Text(f"Error: {str(e)}")
            page.snack_bar.open = True
            page.update()
    def search_by_id(e):
        user_id = search_id_field.value
        if not user_id.isdigit():
            page.snack_bar.content = ft.Text("Por favor, ingresa un ID válido.")
            page.snack_bar.open = True
            page.update()
            search_id_field.value = ""
            return
        try:
            user = fetch_user_by_id(user_id)
            usuarios_table.rows.clear()  
            for u in user:  
                usuarios_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(u["id_usr"]))),
                    ft.DataCell(ft.Text(u["nombre"])),
                    ft.DataCell(ft.Text(u["apellido"])),
                    ft.DataCell(ft.Text(u["username"])),
                    ft.DataCell(ft.Text(u["rol"])),
                    ft.DataCell(ft.Text("Activo" if u["activo"] else "Inactivo")),
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, user=u: edit_user(u))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, user=u: confirm_delete(u["id_usr"]))),
                ]))
            page.snack_bar.content = ft.Text(f"Usuario con ID {user_id} cargado exitosamente.")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}")
        page.snack_bar.open = True
        search_id_field.value = ""
        page.update()

    def search_by_username(e):
        username = search_username_field.value.strip()
        if not username:
            page.snack_bar.content = ft.Text("Por favor, ingresa un username válido.")
            page.snack_bar.open = True
            page.update()
            search_username_field.value = ""
            return
        try:
            user = fetch_user_by_username(username)
            usuarios_table.rows.clear()  
            for u in user:  
                usuarios_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(u["id_usr"]))),
                    ft.DataCell(ft.Text(u["nombre"])),
                    ft.DataCell(ft.Text(u["apellido"])),
                    ft.DataCell(ft.Text(u["username"])),
                    ft.DataCell(ft.Text(u["rol"])),
                    ft.DataCell(ft.Text("Activo" if u["activo"] else "Inactivo")),
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, user=u: edit_user(u))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, user=u: confirm_delete(u["id_usr"]))),
                ]))
            page.snack_bar.content = ft.Text(f"Usuario con username '{username}' cargado exitosamente.")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}")
        page.snack_bar.open = True
        search_username_field.value = ""
        page.update()

    def cancel_edit():
        edit_line.visible = False
        edit_line2.visible = False
        edit_line3.visible = False
        page.update()

    def edit_user(user):
        load_roles_to_dropdown()
        cancel_add()
        global selected_user
        selected_user = user
        name_field.value = user["nombre"]
        last_name_field.value = user["apellido"]
        username_field.value = user["username"]
        role_dropdown.value = user["rol"]
        active_dropdown.value = "Activo" if user["activo"] else "Inactivo" 
        password_field.value = "" 
        edit_line.visible = True
        edit_line2.visible = True
        edit_line3.visible = True
        page.update()

    def confirm_delete(user_id):
        global selected_user_id
        selected_user_id = user_id
        delete_dialog.open = True  
        page.update()
    def load_roles_to_dropdown():
        global roles_global
        roles_global = fetch_roles()  
        role_dropdown.options = [ft.dropdown.Option(rol["descripcion"]) for rol in roles_global]
        page.update()  
    def close_delete_dialog():
        delete_dialog.open = False  
        page.update()  
    def show_add_fields(e):
        load_roles_to_dropdown()
        try:
            cancel_edit()  
            add_line.visible = True
            add_line2.visible = True
            add_line3.visible = True
            if not roles_global:
                raise Exception("No se han cargado los roles correctamente.")
            add_role_dropdown.options = [
                ft.dropdown.Option(role["descripcion"]) for role in roles_global
            ]
            add_active_dropdown.value = "Activo"
            
            page.update()
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al mostrar campos: {ex}")
            page.snack_bar.open = True
            page.update()

    def cancel_add(e=None):  
        add_line.visible = False
        add_line2.visible = False
        add_line3.visible = False
        add_name_field.value = ""
        add_last_name_field.value = ""
        add_username_field.value = ""
        add_password_field.value = ""
        add_role_dropdown.value = None
        add_active_dropdown.value = None
        page.update()

    def save_new_user(e):
        try:
            if not roles_global:
                raise Exception("Los roles no se han cargado correctamente.")

            selected_role = next(
                (role for role in roles_global if role["descripcion"] == add_role_dropdown.value),
                None
            )
            if selected_role is None:
                raise Exception("Seleccione un rol válido.")
            new_user_data = {
                "nombre": add_name_field.value.strip(),
                "apellido": add_last_name_field.value.strip(),
                "username": add_username_field.value.strip(),
                "password": add_password_field.value.strip(),  
                "id_rol": selected_role["id_rol"],
                "activo": add_active_dropdown.value == "Activo",  
            }
            if not all(new_user_data.values()):
                raise Exception("Todos los campos son obligatorios.")
            response = requests.post(f"{API_BASE_URL}/users2", json=new_user_data)
            if response.status_code == 200:
                page.snack_bar.content = ft.Text("Usuario agregado exitosamente.", color="green")
                load_data() 
            else:
                raise Exception(f"Error al agregar usuario: {response.text}")

        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}", color="red")
            page.snack_bar.open = True

        finally:
            page.update()

    
    edit_line = ft.Row(visible=False, controls=[])
    edit_line2 = ft.Row(visible=False, controls=[])
    edit_line3 = ft.Row(visible=False, controls=[])
    search_id_field = ft.TextField(label="Buscar por ID", width=200)
    search_id_button = ft.IconButton(
        icon=ft.icons.SEARCH,
        on_click=search_by_id,
        tooltip="Buscar por ID"
    )
    search_username_field = ft.TextField(label="Buscar por Username", width=200)
    search_username_button = ft.IconButton(
        icon=ft.icons.SEARCH,
        on_click=search_by_username,
        tooltip="Buscar por Username"
    )
    reload_button = ft.ElevatedButton("Cargar", on_click=load_data)
    delete_dialog = ft.AlertDialog(
        title=ft.Text("Confirmar eliminación"),
        content=ft.Text("¿Está seguro de que desea eliminar este usuario?"),
        actions=[
            ft.TextButton(
                "Cancelar", 
                on_click=lambda _: close_delete_dialog()
            ),  
            ft.TextButton(
                "Eliminar", 
                on_click=lambda _: delete_user(selected_user_id)
            ),  
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    password_field = ft.TextField(label="Contraseña (dejar vacío si no desea cambiarla)")    
    edit_line.controls.append(password_field)
    name_field = ft.TextField(label="Nombre")
    last_name_field = ft.TextField(label="Apellido")
    username_field = ft.TextField(label="Username")
    role_dropdown = ft.Dropdown(
    label="Rol",
    options=[]  
    )
    active_dropdown = ft.Dropdown(
        label="Estado",
        options=[
            ft.dropdown.Option("Activo"),
            ft.dropdown.Option("Inactivo")
        ]
    )
    save_button = ft.ElevatedButton("Guardar", on_click=lambda _: save_changes())
    cancel_button = ft.ElevatedButton("Cancelar", on_click=lambda _: cancel_edit())
    edit_line.controls = [
        name_field,
        last_name_field,
        username_field,
    ]
    edit_line2.controls = [        
        role_dropdown,
        password_field,
        active_dropdown,
    ]
    edit_line3.controls = [ 
        save_button,
        cancel_button,
    ]
    add_line = ft.Row(visible=False, controls=[])
    add_line2 = ft.Row(visible=False, controls=[])
    add_line3 = ft.Row(visible=False, controls=[])
    add_name_field = ft.TextField(label="Nombre")
    add_last_name_field = ft.TextField(label="Apellido")
    add_username_field = ft.TextField(label="Username")
    add_password_field = ft.TextField(label="Contraseña")
    add_role_dropdown = ft.Dropdown(
        label="Rol",
        options=[]  
    )
    add_active_dropdown = ft.Dropdown(
    label="Estado",
    options=[
        ft.dropdown.Option("Activo"),
        ft.dropdown.Option("Inactivo"),
    ],
    value="Activo",  
    )
    add_button = ft.ElevatedButton("Agregar Usuario", on_click=show_add_fields)
    save_new_button = ft.ElevatedButton("Agregar", on_click=save_new_user)
    cancel_new_button = ft.ElevatedButton("Cancelar", on_click=cancel_add)

    
    add_line.controls = [
        add_name_field,
        add_last_name_field,
        add_username_field,
    ]
    add_line2.controls = [
        add_role_dropdown,
        add_password_field,
        add_active_dropdown,
    ]
    add_line3.controls = [
        save_new_button,
        cancel_new_button,
    ]

    
    top_row=ft.Row([search_id_field,
                        search_id_button,
                        search_username_field,
                        search_username_button,
                        reload_button,
                        add_button
                        ],
                    spacing=10
                )

    page.snack_bar = ft.SnackBar(
        content=ft.Text(""),
        action="Cerrar",
        open=False
    )
    page.snack_bar.action_button = ft.TextButton(
        "Cerrar",
        on_click=lambda _: setattr(page.snack_bar, "open", False)
    )
    page.dialog = delete_dialog
    page_content = ft.Column([
                navigation_bar(page),
                ft.Text("Usuarios", size=30, weight="bold"),
                top_row,
                usuarios_table,
                add_line,
                add_line2,
                add_line3,
                edit_line,
                edit_line2,
                edit_line3,
            ],scroll=ft.ScrollMode.AUTO
        )
    load_data()
    init_snack_bar()
    
    return page_content

