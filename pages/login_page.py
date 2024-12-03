import flet as ft
import requests
from services.api_client import API_BASE_URL

def login_page(page: ft.Page):
    # Campos de entrada para username y password
    username_field = ft.TextField(label="Username", width=300)
    password_field = ft.TextField(label="Password", password=True, width=300)
    error_message = ft.Text("", color="red")  # Mensaje para errores de login
    
    def handle_login(_):
        username = username_field.value.strip()
        password = password_field.value.strip()
        
        # Validar que los campos no estén vacíos
        if not username or not password:
            error_message.value = "Por favor, llena todos los campos."
            page.update()
            return
        
        try:
            # Realizar solicitud de login al backend
            response = requests.post(
                f"{API_BASE_URL}/login",
                json={"username": username, "password": password}
            )
            print(response)
            response.raise_for_status()  # Levanta excepción si la respuesta tiene error HTTP
            data = response.json()  # Decodificar la respuesta JSON
            print(data)

            # Manejo de roles basado en la respuesta del backend
            if "role" in data and "username" in data:
                role = data["role"]
                id = data["id"]
                user = data["username"]  # Obtener el username de la respuesta
                page.session.set("is_authenticated", True)  # Marcar autenticación exitosa
                page.session.set("user_role", role)  # Guardar el rol del usuario
                page.session.set("username", user)  # Guardar el nombre de usuario en la sesión
                page.session.set("user_id", id)  # Guardar el nombre de usuario en la sesión
                page.go("/")  # Redirigir a la página de inicio
            else:
                error_message.value = "Rol o username no especificados en la respuesta del servidor."
        except requests.exceptions.RequestException as e:
            # Manejo de errores de conexión o solicitud
            error_message.value = f"Error al conectar: {e}"
        except Exception as e:
            # Manejo de errores inesperados
            error_message.value = f"Error inesperado: {e}"

        page.update()  # Actualizar la vista para reflejar cambios

    # Vista de login
    return ft.View(
        "/login",
        [
            ft.Column(
                [
                    ft.Text("FDB135", size=40, weight="bold"),
                    ft.Text("(admin:admin)", size=16, italic=True, color="gray"),
                    username_field,
                    password_field,
                    ft.ElevatedButton("Login", on_click=handle_login),
                    error_message
                ],
                alignment=ft.MainAxisAlignment.CENTER,  # Centrado vertical
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centrado horizontal
                expand=True  # Asegura que la columna ocupe el espacio completo disponible
            )
        ],
        padding=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )


