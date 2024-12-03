
import flet as ft
from components.utils import navigation_bar
import requests
from services.api_client import API_BASE_URL
fetch_vehiculo = []
selected_vehiculo = None
selected_vehiculo_id = None

# Declaración de variables globales
tipo_combustible_global = []

def vehiculo_page(page: ft.Page):
    page.title = "Vehículos"
    page.padding = 10
    

    vehiculo_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("MODELO", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("MARCA", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("PLACA", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("RENDIMIENTO", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("GALONAJE", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("TIPO COMBUSTIBLE", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("Editar", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("Eliminar", style=ft.TextStyle(size=12))),
        ],
        rows=[],  # Aquí puedes agregar filas con estilo reducido
        divider_thickness=0.5,  # Reduce el grosor de las líneas divisorias
        heading_row_height=35,  # Controla la altura de las cabeceras
    )
    def fetch_vehiculo_data():
        try:
            response = requests.get(f"{API_BASE_URL}/vehiculos2")
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            page.snack_bar.content = ft.Text(f"Error al cargar vehículos: {e}")
            page.snack_bar.open = True
            page.update()
            return []

    def fetch_vehiculo_by_id(vehiculo_id):
        cancel_add() 
        try:
            response = requests.get(f"{API_BASE_URL}/vehiculos2/{vehiculo_id}")
            response.raise_for_status()
            return [response.json()]  
        except requests.RequestException as e:
            raise Exception(f"Error al buscar vehículo por ID: {e}")
    
    def delete_vehiculo(id):
        try:
            if id is None:
                raise Exception("No se ha seleccionado un vehículo para eliminar.")
            
            close_delete_dialog()
            response = requests.delete(f"{API_BASE_URL}/vehiculos/{id}")
            if response.status_code == 204:
                page.snack_bar.content = ft.Text("Vehículo eliminado exitosamente.")
                load_data()
            else:
                raise Exception(f"Error al eliminar vehículo. Respuesta: {response.status_code}")
        
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al eliminar vehículo: {ex}")
        
        page.snack_bar.open = True
        page.update()

    def save_changes():
        try:
            global selected_vehiculo, tipo_combustible_global
            if not selected_vehiculo:
                raise Exception("No se ha seleccionado un vehículo para editar.")

            required_fields = {
                "modelo": edit_modelo_field.value.strip(),
                "marca": edit_marca_field.value,
                "placa": edit_placa_field.value,
                "rendimiento": edit_rendimiento_field.value,
                "galonaje": edit_galonaje_field.value,
                "descripcion": edit_descripcion_dropdown.value.strip(),
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    raise Exception(f"El campo '{field_name}' es obligatorio.")
            id_tipo_combustible = next(
                (tc["id_tipo_combustible"] for tc in tipo_combustible_global if tc["descripcion"] == required_fields["descripcion"]),
                None
            )

            if not all([id_tipo_combustible]):
                raise Exception("No se pudo mapear uno o más valores seleccionados a sus IDs correspondientes.")

            updated_data = {
                "id_vehiculo": selected_vehiculo["id_vehiculo"],
                "modelo": str(required_fields["modelo"]),
                "marca": str(required_fields["marca"]),
                "placa": str(required_fields["placa"]),
                "rendimiento": float(required_fields["rendimiento"]),
                "galonaje": float(required_fields["galonaje"]),
                "id_tipo_combustible": id_tipo_combustible,
            }
            url = f"{API_BASE_URL}/vehiculos/{updated_data['id_vehiculo']}"
            response = requests.put(url, json=updated_data)

            if response.status_code == 200:
                edit_line.visible = False
                edit_line2.visible = False
                edit_line3.visible = False
                page.snack_bar.content = ft.Text("Vehículo editado exitosamente.", color="green")
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


    def load_tipo_combustible_dropdown():
        global tipo_combustible_global
        tipo_combustible_global = fetch_tipos_combustible_data()
        add_descripcion_dropdown.options = [ft.dropdown.Option(tc["descripcion"]) for tc in tipo_combustible_global]
        edit_descripcion_dropdown.options = [ft.dropdown.Option(tc["descripcion"]) for tc in tipo_combustible_global]
        page.update()

    def load_data(e=None):
        global fetch_vehiculo
        try:
            cancel_add()
            cancel_edit()
            load_tipo_combustible_dropdown()
            initialize_snack_bar()
            
            page.snack_bar.content = ft.Text("Cargando vehículos desde el backend...")
            page.snack_bar.open = True
            page.update()

            fetch_vehiculo = fetch_vehiculo_data()

            if not fetch_vehiculo:
                page.snack_bar.content = ft.Text("No se encontraron vehículos.")
                page.snack_bar.open = True
                page.update()
                return
            
            vehiculo_table.rows.clear()

            for vehiculo in fetch_vehiculo:
                required_fields = {
                    'id_vehiculo': vehiculo.get('id_vehiculo'),
                    "modelo": vehiculo.get("modelo"),
                    "marca": vehiculo.get("marca"),
                    "placa": vehiculo.get("placa"),
                    "rendimiento": vehiculo.get("rendimiento"),
                    "galonaje": vehiculo.get("galonaje"),
                    "descripcion": vehiculo.get("descripcion"),
                }
                for field_name, field_value in required_fields.items():
                    if field_value is None: 
                        print(f"Falta el campo: {field_name}") 
                        continue
                vehiculo_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(vehiculo["id_vehiculo"]))),
                    ft.DataCell(ft.Text(str(vehiculo["modelo"]))),
                    ft.DataCell(ft.Text(str(vehiculo["marca"]))),
                    ft.DataCell(ft.Text(vehiculo["placa"])),
                    ft.DataCell(ft.Text(str(vehiculo["rendimiento"]))),
                    ft.DataCell(ft.Text(str(vehiculo["galonaje"]))),
                    ft.DataCell(ft.Text(vehiculo["descripcion"])),
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, vehiculo=vehiculo: edit_vehiculo(vehiculo))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, vehiculo=vehiculo: confirm_delete(vehiculo["id_vehiculo"]))),
                ]))
            page.snack_bar.content = ft.Text("Vehículos cargados exitosamente.")
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            page.snack_bar.content = ft.Text(f"Error: {str(e)}")
            page.snack_bar.open = True
            page.update()

    def search_by_id(e):
        cancel_add() 
        cancel_edit() 
        vehiculo_id = search_id_field.value
        if not vehiculo_id.isdigit():
            page.snack_bar.content = ft.Text("Por favor, ingresa un ID válido.")
            page.snack_bar.open = True
            page.update()
            search_id_field.value = ""
            return
        try:
            vehiculo = fetch_vehiculo_by_id(vehiculo_id)
            vehiculo_table.rows.clear()  
            for v in vehiculo:
                vehiculo_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(v["id_vehiculo"]))),
                    ft.DataCell(ft.Text(v["modelo"])),
                    ft.DataCell(ft.Text(str(v["marca"]))),
                    ft.DataCell(ft.Text(str(v["placa"]))),
                    ft.DataCell(ft.Text(str(v["rendimiento"]))),
                    ft.DataCell(ft.Text(str(v["galonaje"]))),
                    ft.DataCell(ft.Text(v["descripcion"])),
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, vehiculo=v: edit_vehiculo(v))),  
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, vehiculo=v: confirm_delete(v["id_vehiculo"]))),  
                ]))
            
            page.snack_bar.content = ft.Text(f"Vehículo con ID {vehiculo_id} cargado exitosamente.")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}")
        page.snack_bar.open = True
        search_id_field.value = ""
        page.update()

    def save_new_vehiculo(e):
        global tipo_combustible_global
        tipo_combustible_global = fetch_tipos_combustible_data()
        
        try:
            required_fields = {
                "modelo": add_modelo_field.value.strip(),
                "marca": add_marca_field.value.strip(),
                "placa": add_placa_field.value.strip(),
                "rendimiento": add_rendimiento_field.value.strip(),
                "galonaje": add_galonaje_field.value.strip(),
                "descripcion": add_descripcion_dropdown.value.strip(),
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    raise Exception(f"El campo '{field_name}' es obligatorio.")
            id_tipo_combustible = next(
                (tc["id_tipo_combustible"] for tc in tipo_combustible_global if tc["descripcion"] == required_fields["descripcion"]),
                None
            )
            if None in [id_tipo_combustible]:
                raise Exception("Alguno de los elementos seleccionados no tiene un ID válido.")
            
            new_vehiculo_data = {
                "id_vehiculo": 0,
                "modelo": required_fields["modelo"],
                "marca": required_fields["marca"],
                "placa": required_fields["placa"],
                "rendimiento": required_fields["rendimiento"],
                "galonaje": required_fields["galonaje"],
                "id_tipo_combustible": id_tipo_combustible,
            }

            response = requests.post(f"{API_BASE_URL}/vehiculos", json=new_vehiculo_data)
            
            if response.status_code == 200:
                page.snack_bar.content = ft.Text("Vehículo agregado exitosamente.", color="green")
                load_data()  # Recargar los datos
            else:
                raise Exception(f"Error al agregar vehículo: {response.text}")

        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}", color="red")
            page.snack_bar.open = True
        finally:
            page.update()


    def show_add_fields(e):
        load_tipo_combustible_dropdown()
        cancel_edit()
        add_modelo_field.value = ""
        add_marca_field.value = ""
        add_placa_field.value = ""
        add_rendimiento_field.value = ""
        add_galonaje_field.value = ""
        add_descripcion_dropdown.value = None
        add_line.visible = True
        add_line2.visible = True
        add_line3.visible = True
        page.update()

    def cancel_edit():
        edit_line.visible = False
        edit_line2.visible = False
        edit_line3.visible = False
        page.update()

    def edit_vehiculo(vehiculo):
        load_tipo_combustible_dropdown()
        cancel_add() 
        global selected_vehiculo
        selected_vehiculo = vehiculo
        edit_modelo_field.value = vehiculo["modelo"]
        edit_marca_field.value = vehiculo["marca"]
        edit_placa_field.value = vehiculo["placa"]
        edit_rendimiento_field.value = vehiculo["rendimiento"]
        edit_galonaje_field.value = vehiculo["galonaje"]        
        edit_descripcion_dropdown.value = vehiculo["descripcion"]
        edit_line.visible = True
        edit_line2.visible = True
        edit_line3.visible = True
        page.update()

    def confirm_delete(vehiculo_id):
        cancel_add()
        cancel_edit()
        global selected_vehiculo_id
        selected_vehiculo_id = vehiculo_id  
        delete_dialog.open = True
        page.update()

    def close_delete_dialog():
        delete_dialog.open = False
        page.update()

    def cancel_add(e=None):
        add_line.visible = False
        add_line2.visible = False
        add_line3.visible = False
        add_modelo_field.value = ""
        add_marca_field.value = ""
        add_placa_field.value = ""
        add_rendimiento_field.value = ""
        add_galonaje_field.value = ""
        add_descripcion_dropdown.value = None
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

    reload_button = ft.ElevatedButton("Cargar", on_click=load_data)
    add_button = ft.ElevatedButton("Agregar Vehículo", on_click=show_add_fields)

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
        content=ft.Text("¿Está seguro de que desea eliminar este vehículo?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: close_delete_dialog()),
            ft.TextButton("Eliminar", on_click=lambda _: delete_vehiculo(selected_vehiculo_id)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    edit_modelo_field = ft.TextField(label="Modelo")
    edit_marca_field = ft.TextField(label="Marca")
    edit_placa_field = ft.TextField(label="Placa")
    edit_rendimiento_field = ft.TextField(label="Rendimiento")
    edit_galonaje_field = ft.TextField(label="Galonaje")
    edit_descripcion_dropdown = ft.Dropdown(
        label="Tipo Combustible",
        options=[]
    )
    save_button = ft.ElevatedButton("Guardar", on_click=lambda _: save_changes())
    cancel_button = ft.ElevatedButton("Cancelar", on_click=lambda _: cancel_edit())

    edit_line.controls = [
        edit_modelo_field,
        edit_marca_field,
        edit_placa_field,    
    ]
    edit_line2.controls = [
        edit_rendimiento_field,
        edit_galonaje_field,
        edit_descripcion_dropdown,  
    ]
    edit_line3.controls = [
        save_button,
        cancel_button,  
    ]

    add_modelo_field = ft.TextField(label="Modelo")
    add_marca_field = ft.TextField(label="Marca")
    add_placa_field = ft.TextField(label="Placa")
    add_rendimiento_field = ft.TextField(label="Rendimiento")
    add_galonaje_field = ft.TextField(label="Galonaje")
    add_descripcion_dropdown = ft.Dropdown(
        label="Tipo Combustible",
        options=[]
    )
    save_new_button = ft.ElevatedButton("Agregar", on_click=save_new_vehiculo)
    cancel_new_button = ft.ElevatedButton("Cancelar", on_click=cancel_add)

    add_line = ft.Row(visible=False, controls=[add_modelo_field, add_marca_field, add_placa_field])
    add_line2 = ft.Row(visible=False, controls=[add_rendimiento_field, add_galonaje_field, add_descripcion_dropdown])
    add_line3 = ft.Row(visible=False, controls=[save_new_button, cancel_new_button])

    vehiculo_table_row = ft.Row(
        controls=[vehiculo_table]
    )
    
    page_content = ft.Column([navigation_bar(page),ft.Text("Vehiculos", size=30, weight="bold"),
        top_row,  
        vehiculo_table_row, 
        edit_line,
        edit_line2, 
        edit_line3,
        add_line,  
        add_line2,  
        add_line3,  
        delete_dialog 
    ],scroll=ft.ScrollMode.AUTO)
    initialize_snack_bar()
    load_data() 
    return page_content