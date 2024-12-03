import flet as ft

def navigation_bar(page: ft.Page):
    """Barra de navegación común para todas las páginas."""
    def handle_logout(e):
        page.session.set("is_authenticated",False)  # Cierra sesión
        page.go("/login")  # Redirige al login


    return ft.Row(
        controls=[
            ft.ElevatedButton("Home", on_click=lambda _: page.go("/")),
            ft.ElevatedButton("Logs", on_click=lambda _: page.go("/logs")),
            ft.ElevatedButton("Roles", on_click=lambda _: page.go("/roles")),
            ft.ElevatedButton("Vehiculos", on_click=lambda _: page.go("/vehiculos")),
            ft.ElevatedButton("Gasolineras", on_click=lambda _: page.go("/gasolineras")),
            ft.ElevatedButton("Proyectos", on_click=lambda _: page.go("/proyectos")),
            ft.ElevatedButton("Usuarios", on_click=lambda _: page.go("/users")),
            ft.ElevatedButton("Bitacora", on_click=lambda _: page.go("/bitacora")),
            ft.ElevatedButton("Tipo Combustible", on_click=lambda _: page.go("/tipo_combustible")),
            ft.ElevatedButton("Logout", on_click=handle_logout, style=ft.ButtonStyle(bgcolor=ft.colors.RED, color=ft.colors.WHITE))
        ],
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        spacing=10,
        height=50,
    )
