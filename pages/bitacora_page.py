import flet as ft
import requests
from components.utils import navigation_bar
from services.api_client import API_BASE_URL
fetch_bitacora = []
selected_bitacora = None
selected_bitacora_id = None
tipo_combustible_global = []
username_global = []
vehiculo_global = []
gasolinera_global = []
proyecto_global = []


def bitacora_page(page: ft.Page):
    page.title = "Bitacora"
    page.padding = 10
    

    bitacora_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("KmInit", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("KmEnd", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("Coment", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("NumGal", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("Price", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("TipeCom", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("UserName", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("PlacaVehiculo", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("Gasolinera", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("Proyecto", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("Editar", style=ft.TextStyle(size=12))),
            ft.DataColumn(ft.Text("Eliminar", style=ft.TextStyle(size=12))),
        ],
        rows=[],  
        divider_thickness=0.0,
        heading_row_height=35,
    )

    def fetch_bitacora_data():
        try:
            response = requests.get(f"{API_BASE_URL}/bitacora2")
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            page.snack_bar.content = ft.Text(f"Error al cargar bitacoras: {e}")
            page.snack_bar.open = True
            page.update()
            return []

    def fetch_bitacora_by_id(bitacora_id):
        cancel_add() 
        cancel_edit
        try:
            response = requests.get(f"{API_BASE_URL}/bitacora2/{bitacora_id}")
            response.raise_for_status()
            return [response.json()]  
        except requests.RequestException as e:
            raise Exception(f"Error al buscar bitacora por ID: {e}")
    
    def delete_bitacora(id):
        try:
            if id is None:
                raise Exception("No se ha seleccionado un bitacora para eliminar.")
            
            close_delete_dialog()
            response = requests.delete(f"{API_BASE_URL}/bitacora/{id}")
            if response.status_code == 204:
                page.snack_bar.content = ft.Text("Bitacora eliminado exitosamente.")
                load_data()
            else:
                raise Exception(f"Error al eliminar bitacora. Respuesta: {response.status_code}")
        
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error al eliminar bitacora: {ex}")
        
        page.snack_bar.open = True
        page.update()

    def save_changes():
        try:
            global selected_bitacora, tipo_combustible_global, username_global, vehiculo_global, gasolinera_global, proyecto_global

            
            if not selected_bitacora:
                raise Exception("No se ha seleccionado una bitácora para editar.")

            
            required_fields = {
                "comentario": edit_comentario_field.value.strip(),
                "km_inicial": edit_km_inicial_field.value,
                "km_final": edit_km_final_field.value,
                "num_galones": edit_num_galones_field.value,
                "costo": edit_costo_field.value,
                "descripcion_tipo_combustible": edit_descripcion_tipo_combustible_dropdown.value.strip(),
                "username": edit_username_dropdown.value.strip(),
                "placa_vehiculo": edit_placa_vehiculo_dropdown.value.strip(),
                "nombre_gasolinera": edit_nombre_gasolinera_dropdown.value.strip(),
                "nombre_proyecto": edit_nombre_proyecto_dropdown.value.strip(),
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    raise Exception(f"El campo '{field_name}' es obligatorio.")

            
            id_tipo_combustible = next(
                (tc["id_tipo_combustible"] for tc in tipo_combustible_global if tc["descripcion"] == required_fields["descripcion_tipo_combustible"]),
                None
            )
            id_usr = next(
                (usr["id_usr"] for usr in username_global if usr["username"] == required_fields["username"]),
                None
            )
            id_vehiculo = next(
                (veh["id_vehiculo"] for veh in vehiculo_global if veh["placa"] == required_fields["placa_vehiculo"]),
                None
            )
            id_gasolinera = next(
                (gas["id_gasolinera"] for gas in gasolinera_global if gas["nombre"] == required_fields["nombre_gasolinera"]),
                None
            )
            id_proyecto = next(
                (proj["id_proyecto"] for proj in proyecto_global if proj["nombre"] == required_fields["nombre_proyecto"]),
                None
            )

            
            if not all([id_tipo_combustible, id_usr, id_vehiculo, id_gasolinera, id_proyecto]):
                raise Exception("No se pudo mapear uno o más valores seleccionados a sus IDs correspondientes.")

            
            updated_data = {
                "id_bitacora": selected_bitacora["id_bitacora"],
                "comentario": required_fields["comentario"],
                "km_inicial": int(required_fields["km_inicial"]),
                "km_final": int(required_fields["km_final"]),
                "num_galones": float(required_fields["num_galones"]),
                "costo": float(required_fields["costo"]),
                "id_tipo_combustible": id_tipo_combustible,
                "id_usr": id_usr,
                "id_vehiculo": id_vehiculo,
                "id_gasolinera": id_gasolinera,
                "id_proyecto": id_proyecto,
            }

            
            url = f"{API_BASE_URL}/bitacora/{updated_data['id_bitacora']}"
            response = requests.put(url, json=updated_data)

            if response.status_code == 200:
                cancel_edit
                page.snack_bar.content = ft.Text("Bitácora editada exitosamente.", color="green")
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

    def fetch_all_data():
            try:
                # Realizamos la solicitud GET al endpoint que devuelve todos los datos
                response = requests.get(f"{API_BASE_URL}/data")
                response.raise_for_status()  # Verifica si la solicitud fue exitosa (status 200)
                
                # Obtener los datos en formato JSON
                data = response.json()

                # Extraemos cada sección de datos (usuarios, gasolineras, tipos de combustible, proyectos, vehículos)
                users = data.get("users", [])
                gasolineras = data.get("gasolineras", [])
                tipos_combustible = data.get("tipos_combustible", [])
                proyectos = data.get("proyectos", [])
                vehiculos = data.get("vehiculos", [])

                # Devuelve los datos extraídos
                return {
                    "users": users,
                    "gasolineras": gasolineras,
                    "tipos_combustible": tipos_combustible,
                    "proyectos": proyectos,
                    "vehiculos": vehiculos
                }

            except requests.exceptions.RequestException as e:
                # Manejo de errores si la solicitud falla
                page.snack_bar.content = ft.Text(f"Error al cargar los datos: {e}")
                page.snack_bar.open = True
                page.update()
                return {
                    "users": [],
                    "gasolineras": [],
                    "tipos_combustible": [],
                    "proyectos": [],
                    "vehiculos": []
                }

    def load_roles_to_dropdown():
        # Cargar todos los datos usando la nueva función fetch_all_data
        global tipo_combustible_global, username_global, vehiculo_global, gasolinera_global, proyecto_global

        # Llamada a la función que obtiene todos los datos
        all_data = fetch_all_data()

        # Asignar los datos a las variables globales
        tipo_combustible_global = all_data["tipos_combustible"]
        username_global = all_data["users"]
        vehiculo_global = all_data["vehiculos"]
        gasolinera_global = all_data["gasolineras"]
        proyecto_global = all_data["proyectos"]
        add_descripcion_tipo_combustible_dropdown.options = [ft.dropdown.Option(tc["descripcion_tipo_combustible"]) for tc in tipo_combustible_global]
        add_username_dropdown.options = [ft.dropdown.Option(user["username"]) for user in username_global]
        add_placa_vehiculo_dropdown.options = [ft.dropdown.Option(vehiculo["placa_vehiculo"]) for vehiculo in vehiculo_global]
        add_nombre_gasolinera_dropdown.options = [ft.dropdown.Option(gasolinera["nombre_gasolinera"]) for gasolinera in gasolinera_global]
        add_nombre_proyecto_dropdown.options = [ft.dropdown.Option(proyecto["nombre_proyecto"]) for proyecto in proyecto_global]
        edit_descripcion_tipo_combustible_dropdown.options = [ft.dropdown.Option(tc["descripcion_tipo_combustible"]) for tc in tipo_combustible_global]
        edit_username_dropdown.options = [ft.dropdown.Option(user["username"]) for user in username_global]
        edit_placa_vehiculo_dropdown.options = [ft.dropdown.Option(vehiculo["placa_vehiculo"]) for vehiculo in vehiculo_global]
        edit_nombre_gasolinera_dropdown.options = [ft.dropdown.Option(gasolinera["nombre_gasolinera"]) for gasolinera in gasolinera_global]
        edit_nombre_proyecto_dropdown.options = [ft.dropdown.Option(proyecto["nombre_proyecto"]) for proyecto in proyecto_global]
        
        
        

    def load_data(e=None):
        global fetch_bitacora
        try:
            cancel_edit()
            cancel_add()         
            page.snack_bar.content = ft.Text("Cargando bitacoras desde el backend...")
            page.snack_bar.open = True
            page.update()
            
            fetch_bitacora = fetch_bitacora_data()

            if not fetch_bitacora:
                page.snack_bar.content = ft.Text("No se encontraron bitacoras.")
                page.snack_bar.open = True
                page.update()
                return
            
            bitacora_table.rows.clear()

            for bitacora in fetch_bitacora:
                required_fields = {
                    'id_bitacora': bitacora['id_bitacora'],
                    "km_inicial": bitacora["km_inicial"],
                    "km_final": bitacora["km_final"],
                    "comentario": bitacora["comentario"],
                    "num_galones": bitacora["num_galones"],
                    "costo": bitacora["costo"],
                    "descripcion_tipo_combustible": bitacora["descripcion_tipo_combustible"],
                    "username": bitacora["username"],
                    "placa_vehiculo": bitacora["placa_vehiculo"],
                    "nombre_gasolinera": bitacora["nombre_gasolinera"],
                    "nombre_proyecto": bitacora["nombre_proyecto"],
                }

                for field_name, field_value in required_fields.items():
                    if field_name not in bitacora:
                        continue
                bitacora_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(bitacora["id_bitacora"]))),
                    ft.DataCell(ft.Text(str(bitacora["km_inicial"]))),
                    ft.DataCell(ft.Text(str(bitacora["km_final"]))),
                    ft.DataCell(ft.Text(bitacora["comentario"])),
                    ft.DataCell(ft.Text(str(bitacora["num_galones"]))),
                    ft.DataCell(ft.Text(str(bitacora["costo"]))),
                    ft.DataCell(ft.Text(bitacora["descripcion_tipo_combustible"])),
                    ft.DataCell(ft.Text(bitacora["username"])),
                    ft.DataCell(ft.Text(bitacora["placa_vehiculo"])),
                    ft.DataCell(ft.Text(bitacora["nombre_gasolinera"])),
                    ft.DataCell(ft.Text(bitacora["nombre_proyecto"])),
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, bitacora=bitacora: edit_bitacora(bitacora))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, bitacora=bitacora: confirm_delete(bitacora["id_bitacora"]))),
                ]))

            page.snack_bar.content = ft.Text("Bitácoras cargadas exitosamente.")
            page.snack_bar.open = True
            page.update()

        except Exception as e:
            page.snack_bar.content = ft.Text(f"Error: {str(e)}")
            page.snack_bar.open = True
            page.update()

    def search_by_id(e):
        cancel_add() 
        cancel_edit() 
        bitacora_id = search_id_field.value
        if not bitacora_id.isdigit():
            page.snack_bar.content = ft.Text("Por favor, ingresa un ID válido.")
            page.snack_bar.open = True
            page.update()
            search_id_field.value = ""
            return
        try:
            bitacora = fetch_bitacora_by_id(int(bitacora_id))
            
            bitacora_table.rows.clear()  

            for b in bitacora:
                bitacora_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(b["id_bitacora"]))),
                    ft.DataCell(ft.Text(b["comentario"])),
                    ft.DataCell(ft.Text(str(b["km_inicial"]))),
                    ft.DataCell(ft.Text(str(b["km_final"]))),
                    ft.DataCell(ft.Text(str(b["num_galones"]))),
                    ft.DataCell(ft.Text(str(b["costo"]))),
                    ft.DataCell(ft.Text(b["descripcion_tipo_combustible"])),
                    ft.DataCell(ft.Text(b["username"])),
                    ft.DataCell(ft.Text(b["placa_vehiculo"])),
                    ft.DataCell(ft.Text(b["nombre_gasolinera"])),
                    ft.DataCell(ft.Text(b["nombre_proyecto"])),
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, bitacora=b: edit_bitacora(b))),  
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, bitacora=b: confirm_delete(b["id_bitacora"]))),  
                ]))
            
            page.snack_bar.content = ft.Text(f"Bitacora con ID {bitacora_id} cargado exitosamente.")
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}")
        page.snack_bar.open = True
        search_id_field.value = ""
        page.update()

    def save_new_bitacora(e):
        try:
            
            required_fields = {
                "km_inicial": add_km_inicial_field.value.strip(),
                "km_final": add_km_final_field.value.strip(),
                "comentario": add_comentario_field.value.strip(),
                "num_galones": add_num_galones_field.value.strip(),
                "costo": add_costo_field.value.strip(),
                "id_tipo_combustible": add_descripcion_tipo_combustible_dropdown.value.strip(),
                "id_usr": add_username_dropdown.value.strip(),
                "id_vehiculo": add_placa_vehiculo_dropdown.value.strip(),
                "id_gasolinera": add_nombre_gasolinera_dropdown.value.strip(),
                "id_proyecto": add_nombre_proyecto_dropdown.value.strip(),
            }

            
            for field_name, field_value in required_fields.items():
                if not field_value:
                    raise Exception(f"El campo '{field_name}' es obligatorio.")

            
            id_tipo_combustible = next(
                (tc["id_tipo_combustible"] for tc in tipo_combustible_global if tc["descripcion"] == required_fields["id_tipo_combustible"]),
                None
            )
            id_usr = next(
                (usr["id_usr"] for usr in username_global if usr["username"] == required_fields["id_usr"]),
                None
            )
            id_vehiculo = next(
                (veh["id_vehiculo"] for veh in vehiculo_global if veh["placa"] == required_fields["id_vehiculo"]),
                None
            )
            id_gasolinera = next(
                (gas["id_gasolinera"] for gas in gasolinera_global if gas["nombre"] == required_fields["id_gasolinera"]),
                None
            )
            id_proyecto = next(
                (pro["id_proyecto"] for pro in proyecto_global if pro["nombre"] == required_fields["id_proyecto"]),
                None
            )

            
            if None in [id_tipo_combustible, id_usr, id_vehiculo, id_gasolinera, id_proyecto]:
                raise Exception("Alguno de los elementos seleccionados no tiene un ID válido.")

            
            new_bitacora_data = {
                "id_bitacora": 0,
                "km_inicial": required_fields["km_inicial"],
                "km_final": required_fields["km_final"],
                "comentario": required_fields["comentario"],
                "num_galones": required_fields["num_galones"],
                "costo": required_fields["costo"],
                "id_tipo_combustible": id_tipo_combustible,
                "id_usr": id_usr,
                "id_vehiculo": id_vehiculo,
                "id_gasolinera": id_gasolinera,
                "id_proyecto": id_proyecto,
            }

            
            response = requests.post(f"{API_BASE_URL}/bitacora", json=new_bitacora_data)
            if response.status_code == 200:
                page.snack_bar.content = ft.Text("Bitacora agregada exitosamente.", color="green")
                load_data()  
            else:
                raise Exception(f"Error al agregar bitacora: {response.text}")

        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error: {ex}", color="red")
            page.snack_bar.open = True
        finally:
            page.update()

    def show_add_fields(e):
        cancel_edit()
        load_roles_to_dropdown()
        add_km_inicial_field.value = ""
        add_km_final_field.value = ""
        add_comentario_field.value = ""
        add_num_galones_field.value = ""
        add_costo_field.value = ""
        add_descripcion_tipo_combustible_dropdown.value = None
        add_username_dropdown.value = None
        add_placa_vehiculo_dropdown.value = None
        add_nombre_gasolinera_dropdown.value = None
        add_nombre_proyecto_dropdown.value = None
        add_line.visible = True
        add_line2.visible = True
        add_line3.visible = True
        add_line4.visible = True
        page.update()

    def cancel_edit():
        edit_line.visible = False
        edit_line2.visible = False
        edit_line3.visible = False
        edit_line4.visible = False
        edit_km_final_field.value = ""
        edit_km_inicial_field.value = ""
        edit_comentario_field.value = ""
        edit_num_galones_field.value = ""
        edit_costo_field.value = ""
        edit_descripcion_tipo_combustible_dropdown.value = None
        edit_username_dropdown.value = None
        edit_placa_vehiculo_dropdown.value = None
        edit_nombre_gasolinera_dropdown.value = None
        edit_nombre_proyecto_dropdown.value = None
        page.update()

    def edit_bitacora(bitacora):
        cancel_add() 
        load_roles_to_dropdown()
        global selected_bitacora
        selected_bitacora = bitacora
        edit_km_inicial_field.value = bitacora["km_inicial"]
        edit_km_final_field.value = bitacora["km_final"]
        edit_comentario_field.value = bitacora["comentario"]
        edit_num_galones_field.value = bitacora["num_galones"]
        edit_costo_field.value = bitacora["costo"]        
        edit_descripcion_tipo_combustible_dropdown.value = bitacora["descripcion_tipo_combustible"]
        edit_username_dropdown.value = bitacora["username"]
        edit_placa_vehiculo_dropdown.value = bitacora["placa_vehiculo"]
        edit_nombre_gasolinera_dropdown.value = bitacora["nombre_gasolinera"]
        edit_nombre_proyecto_dropdown.value = bitacora["nombre_proyecto"]
        edit_line.visible = True
        edit_line2.visible = True
        edit_line3.visible = True
        edit_line4.visible = True
        page.update()

    def confirm_delete(bitacora_id):
        cancel_add() 
        load_data()  
        global selected_bitacora_id
        selected_bitacora_id = bitacora_id  
        delete_dialog.open = True
        page.update()

    def close_delete_dialog():
        delete_dialog.open = False
        page.update()

    def cancel_add(e=None):
        add_line.visible = False
        add_line2.visible = False
        add_line3.visible = False
        add_line4.visible = False
        add_km_inicial_field.value = ""
        add_km_final_field.value = ""
        add_comentario_field.value = ""
        add_num_galones_field.value = ""
        add_costo_field.value = ""
        add_descripcion_tipo_combustible_dropdown.value = None
        add_username_dropdown.value = None
        add_placa_vehiculo_dropdown.value = None
        add_nombre_gasolinera_dropdown.value = None
        add_nombre_proyecto_dropdown.value = None
        page.update()

    edit_line = ft.Row(visible=False, controls=[])
    edit_line2 = ft.Row(visible=False, controls=[])
    edit_line3 = ft.Row(visible=False, controls=[])
    edit_line4 = ft.Row(visible=False, controls=[])

    search_id_field = ft.TextField(label="Buscar por ID", width=200)
    search_id_button = ft.IconButton(
        icon=ft.icons.SEARCH,
        on_click=search_by_id,
        tooltip="Buscar por ID"
    )
    reload_button = ft.ElevatedButton("Cargar", on_click=load_data)
    add_button = ft.ElevatedButton("Agregar Bitacora", on_click=show_add_fields)

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
        content=ft.Text("¿Está seguro de que desea eliminar esta bitacora?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: close_delete_dialog()),
            ft.TextButton("Eliminar", on_click=lambda _: delete_bitacora(selected_bitacora_id)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    edit_km_inicial_field = ft.TextField(label="KM Inicial")
    edit_km_final_field = ft.TextField(label="KM Final")
    edit_comentario_field = ft.TextField(label="Comentario")
    edit_num_galones_field = ft.TextField(label="Numero Galones")
    edit_costo_field = ft.TextField(label="Costo")
    edit_descripcion_tipo_combustible_dropdown = ft.Dropdown(
        label="Tipo Combustible",
        options=[]
    )
    edit_username_dropdown = ft.Dropdown(
        label="UserName",
        options=[]
    )
    edit_placa_vehiculo_dropdown = ft.Dropdown(
        label="Vehiculo",
        options=[]
    )
    edit_nombre_gasolinera_dropdown = ft.Dropdown(
        label="Gasolinera",
        options=[]
    )
    edit_nombre_proyecto_dropdown = ft.Dropdown(
        label="Proyecto",
        options=[]
    )
    save_button = ft.ElevatedButton("Guardar", on_click=lambda _: save_changes())
    cancel_button = ft.ElevatedButton("Cancelar", on_click=lambda _: cancel_edit())

    edit_line.controls = [
        edit_km_inicial_field,
        edit_km_final_field,
        edit_comentario_field,    
    ]
    edit_line2.controls = [
        edit_num_galones_field,
        edit_costo_field,
        edit_descripcion_tipo_combustible_dropdown,  
    ]
    edit_line3.controls = [
        edit_username_dropdown,
        edit_placa_vehiculo_dropdown,
        edit_nombre_gasolinera_dropdown,  
    ]
    edit_line4.controls = [
        edit_nombre_proyecto_dropdown,
        save_button,
        cancel_button,  
    ]

    add_km_inicial_field = ft.TextField(label="KM Inicial")
    add_km_final_field = ft.TextField(label="KM Final")
    add_comentario_field = ft.TextField(label="Comentario")
    add_num_galones_field = ft.TextField(label="Numero Galones")
    add_costo_field = ft.TextField(label="Costo")
    add_descripcion_tipo_combustible_dropdown = ft.Dropdown(
        label="Tipo Combustible",
        options=[]
    )
    add_username_dropdown = ft.Dropdown(
        label="UserName",
        options=[]
    )
    add_placa_vehiculo_dropdown = ft.Dropdown(
        label="Vehiculo",
        options=[]
    )
    add_nombre_gasolinera_dropdown = ft.Dropdown(
        label="Gasolinera",
        options=[]
    )
    add_nombre_proyecto_dropdown = ft.Dropdown(
        label="Proyecto",
        options=[]
    )
    save_new_button = ft.ElevatedButton("Agregar", on_click=save_new_bitacora)
    cancel_new_button = ft.ElevatedButton("Cancelar", on_click=cancel_add)

    add_line = ft.Row(visible=False, controls=[add_km_inicial_field,add_km_final_field,add_comentario_field])
    add_line2 = ft.Row(visible=False, controls=[add_num_galones_field, add_costo_field,add_descripcion_tipo_combustible_dropdown])
    add_line3 = ft.Row(visible=False, controls=[add_username_dropdown, add_placa_vehiculo_dropdown, add_nombre_gasolinera_dropdown])
    add_line4 = ft.Row(visible=False, controls=[add_nombre_proyecto_dropdown, save_new_button, cancel_new_button])

    bitacora_table_row = ft.Row(
        [bitacora_table],
        scroll=ft.ScrollMode.AUTO
    )
    page_content = ft.View(
        "/bitacora",
        [
            ft.Column(
                [
                    navigation_bar(page),
                    ft.Text("Bitacora", size=30, weight="bold"),
                    top_row,
                    bitacora_table_row,
                    edit_line,
                    edit_line2,
                    edit_line3,
                    edit_line4,
                    add_line,
                    add_line2,
                    add_line3,
                    add_line4,
                    delete_dialog
                ]
            )
        ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centrado horizontal
                scroll=ft.ScrollMode.AUTO
    )


    
    initialize_snack_bar()
    load_data()
    
    return page_content