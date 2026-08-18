import flet
from flet import Container, Page, Row, Text
from route_guard import require_role
from viewmodels.user_viewmodel import UserViewModel
from views.authenticated.acceso_denegado_view import AccesoDenegadoView
from views.authenticated.admin_dashboard_view import AdminDashboardView
from views.authenticated.buscar_complejos_view import BuscarComplejosView
from views.authenticated.canchas_view import CanchasView
from views.authenticated.complejos_view import ComplejosView
from views.authenticated.gestion_reclamos_view import GestionReclamosView
from views.authenticated.mis_datos_view import MisDatosView
from views.authenticated.mis_reclamos_view import MisReclamosView
from views.authenticated.mis_reservas_view import MisReservasView
from views.authenticated.usuario_dashboard_view import UsuarioDashboardView
from views.home_view import HomeView
from views.login_view import LoginView
from views.widgets.navbar import Navbar as LandingNavbar
from views.widgets.navbar_pages import Navbar as AuthenticatedNavbar
from views.widgets.sidebar import Sidebar


def main(page: Page):
    page.title = "ArriendoCancha.cl"
    page.theme_mode = "light"
    page.vertical_alignment = "start"

    user_vm = UserViewModel()

    page.section_ids = {
        "home": "home_section",
        "about": "about_section",
        "services": "services_section",
        "clients": "clients_section",
        "contact": "contact_section",
        "login": "login_section",
    }

    # Estado para controlar la visibilidad del sidebar
    sidebar_visible = False

    # Función para alternar la visibilidad del sidebar
    def toggle_sidebar(e):
        nonlocal sidebar_visible
        sidebar_visible = not sidebar_visible
        route_change(page.route)

    # Función para manejar rutas
    def route_change(route):
        page.controls.clear()

        # --- Usuario autenticado ---
        if user_vm.is_authenticated():

            # Normalizar "/" → "/dashboard" antes de evaluar permisos
            effective_route = (
                "/dashboard" if page.route == "/" else page.route
            )

            # 1) Evaluar permiso mediante route_guard
            guard_result = require_role(user_vm, effective_route)

            # Rama NO_SESSION: limpiar y redirigir a login
            if guard_result == "NO_SESSION":
                user_vm.logout()
                page.go("/login")
                return

            # Rama FORBIDDEN: mostrar acceso denegado
            if guard_result == "FORBIDDEN":
                content = AccesoDenegadoView(page, user_vm)
                page.appbar = AuthenticatedNavbar(
                    page, user_vm, toggle_sidebar
                )
                page.add(
                    Row(
                        controls=[
                            Container(
                                width=200 if sidebar_visible else 0,
                                content=(
                                    Sidebar(page, user_vm)
                                    if sidebar_visible
                                    else None
                                ),
                            ),
                            Container(expand=True, content=content),
                        ],
                        expand=True,
                    )
                )
                page.update()
                return

            # --- OK: usuario autenticado y autorizado ---
            page.appbar = AuthenticatedNavbar(page, user_vm, toggle_sidebar)

            if effective_route == "/dashboard":
                # Dispatch por rol
                rol = user_vm.get_user().get("tipo_cuenta")
                if rol == "Administrador":
                    content = AdminDashboardView(page, user_vm)
                elif rol == "Usuario":
                    content = UsuarioDashboardView(page, user_vm)
                else:
                    content = AccesoDenegadoView(page, user_vm)
            elif effective_route == "/acceso_denegado":
                content = AccesoDenegadoView(page, user_vm)
            elif effective_route == "/mis_complejos":
                content = ComplejosView(page, user_vm)
            elif effective_route == "/mis_canchas":
                content = CanchasView(page, user_vm)
            elif effective_route == "/mis_datos":
                content = MisDatosView(page, user_vm)
            elif effective_route == "/buscar_complejos":
                content = BuscarComplejosView(page, user_vm)
            elif effective_route == "/mis_reservas":
                content = MisReservasView(page, user_vm)
            elif effective_route == "/mis_reclamos":
                content = MisReclamosView(page, user_vm)
            elif effective_route == "/gestion_reclamos":
                content = GestionReclamosView(page, user_vm)
            else:
                content = Text("Página no encontrada")

            # Layout con sidebar
            page.add(
                Row(
                    controls=[
                        Container(
                            width=200 if sidebar_visible else 0,
                            content=(
                                Sidebar(page, user_vm)
                                if sidebar_visible
                                else None
                            ),
                        ),
                        Container(expand=True, content=content),
                    ],
                    expand=True,
                )
            )
        else:
            # Usuario no autenticado
            if page.route == "/login":
                content = LoginView(page, user_vm)
            else:
                content = HomeView(page, user_vm)
            page.appbar = LandingNavbar(page)
            page.add(content)

        page.update()

    # Función para manejar cambios en la ruta
    page.on_route_change = lambda e: route_change(page.route)

    # Establecer ruta inicial
    page.go(page.route or "/")


# Llamada a flet.app fuera de la función main
flet.app(target=main, view="web_browser", port=8555)