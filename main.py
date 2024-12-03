import flet as ft
from pages.home_page import home_page
from pages.login_page import login_page  # Página de login creada previamente
from pages.bitacora_page import bitacora_page
from pages.bitacora_user_page import bitacora_user_page  # Página para usuarios no administradores
from pages.gasolineras_page import gasolineras_page
from pages.log_page import log_page
from pages.proyecto_page import proyecto_page
from pages.rol_page import rol_page
from pages.tipo_combustible_page import tipo_combustible_page
from pages.usuarios_page import usuarios_page
from pages.vehiculo_page import vehiculo_page

def main(page: ft.Page):
    page.title = "Aplicación Multi-Página"
    page.window_max_width
    page.window_max_height
    
    # Comprobar autenticación inicial
    if not page.session.get("is_authenticated"):
        page.session.set("is_authenticated", False)  # Inicializar autenticación
        page.session.set("user_role", "user")  # Por defecto, rol 'user'

    def route_change(route):
        """Maneja los cambios de ruta y carga las vistas correspondientes."""
        page.views.clear()

        # Redirigir a login si no está autenticado
        if not page.session.get("is_authenticated"):
            page.session.set("is_authenticated", False)
        
        if not page.session.get("is_authenticated") and page.route != "/login":
            page.go("/login")
            return

        # Obtener el rol del usuario desde la sesión
        user_role = page.session.get("user_role")  # Intenta obtener el rol
        if user_role is None:  # Si no existe, asigna un valor predeterminado
            user_role = "user"

        # Validación de acceso basado en rol
        if user_role != "admin" and page.route not in ["/bitacora_user", "/login", "/"]:
            page.go("/bitacora_user")  # Redirigir a la página de bitácora para usuarios no admin
            return

        # Rutas disponibles
        if page.route == "/login":
            page.views.append(login_page(page))
        elif page.route == "/":
            page.views.append(home_page(page))
        elif page.route == "/vehiculos":
            page.views.append(vehiculo_page(page))
        elif page.route == "/roles":
            page.views.append(rol_page(page))
        elif page.route == "/tipo_combustible":
            page.views.append(tipo_combustible_page(page))
        elif page.route == "/logs":
            page.views.append(log_page(page))
        elif page.route == "/proyectos":
            page.views.append(proyecto_page(page))
        elif page.route == "/gasolineras":
            page.views.append(gasolineras_page(page))
        elif page.route == "/users":
            page.views.append(usuarios_page(page))
        elif page.route == "/bitacora":
            page.views.append(bitacora_page(page))
        elif page.route == "/bitacora_user":
            page.views.append(bitacora_user_page(page))
        else:
            page.views.append(ft.View("/404", [ft.Text("Página no encontrada")]))
        page.update()

    # Registrar el manejador de cambios de ruta
    page.on_route_change = route_change
    # Configurar la ruta inicial o mantener la existente
    page.go(page.route or "/")  

ft.app(target=main, view=ft.WEB_BROWSER)