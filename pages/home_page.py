import flet as ft
from components.utils import navigation_bar

def home_page(page: ft.Page):
    # Obtener el rol y el nombre de usuario desde la sesión
    user_role = page.session.get("user_role")  # Obtener el rol del usuario
    username = page.session.get("username")  # Obtener el nombre de usuario desde la sesión
    print(username)

    if user_role is None:  # Si no existe el rol, asignamos el rol por defecto
        user_role = "user"

    # Mensaje de bienvenida y controles según el rol
    if user_role == "admin":
        welcome_message = ft.Text(
            "Bienvenido Administrador "+username+" al sistema de gestión de combustible", size=30
        )
        restrictions_message = None
        controls = []  # El administrador tiene acceso completo, por lo que no necesitamos restringir los controles
    else:
        welcome_message = ft.Text(
            f"Bienvenido Usuario {username} al sistema de gestión de combustible", size=30
        )
        restrictions_message = ft.Text(
            "Advertencia: No puedes acceder a otras páginas excepto Bitácora. "
            "Solo puedes agregar y editar registros bajo tu nombre.",
            color="red", size=20
        )
        controls = [
            ft.ElevatedButton("Ir a Bitácora", on_click=lambda _: page.go("/bitacora_user"))
        ]

    # Devolver la vista con los elementos definidos
    return ft.View(
        "/",
        controls=[
            navigation_bar(page),  # Barra de navegación superior
            welcome_message,
            restrictions_message if restrictions_message else ft.Container(),  # Mostrar mensaje de advertencia si es usuario
            *controls  # Mostrar controles adicionales solo si es un usuario
        ],
    )



