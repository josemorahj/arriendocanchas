# views/widgets/sidebar.py

from flet import Column, ListTile, Icon, icons, Text

def Sidebar(page, user_vm):
    def navigate_to(route):
        page.go(route)
        page.update()

    user = user_vm.get_user()
    user_type = user['tipo_cuenta']

    controls = []

    # Común para todos los usuarios
    controls.append(
        ListTile(
            leading=Icon(icons.HOME),
            title=Text("Inicio"),
            on_click=lambda e: navigate_to("/dashboard"),
        )
    )

    # Elementos basados en el tipo de usuario
    if user_type == "Administrador":
        controls.extend([
            ListTile(
                leading=Icon(icons.BUSINESS),
                title=Text("Mis Complejos"),
                on_click=lambda e: navigate_to("/mis_complejos"),
            ),
                        ListTile(
                leading=Icon(icons.SPORTS_SOCCER),
                title=Text("Mis Canchas"),
                on_click=lambda e: navigate_to("/mis_canchas"),
            ),
            ListTile(
                leading=Icon(icons.REPORT),
                title=Text("Gestionar Reclamos"),
                on_click=lambda e: navigate_to("/gestion_reclamos"),
            ),
        ])
    elif user_type == "Usuario":
        controls.extend([
            ListTile(
                leading=Icon(icons.ACCOUNT_BOX),
                title=Text("Mis Datos"),
                on_click=lambda e: navigate_to("/mis_datos"),
            ),
            ListTile(
                leading=Icon(icons.SEARCH),
                title=Text("Buscar Complejos"),
                on_click=lambda e: navigate_to("/buscar_complejos"),
            ),
            ListTile(
                leading=Icon(icons.BOOKMARK),
                title=Text("Mis Reservas"),
                on_click=lambda e: navigate_to("/mis_reservas"),
            ),
            ListTile(
                leading=Icon(icons.REPORT),
                title=Text("Mis Reclamos"),
                on_click=lambda e: navigate_to("/mis_reclamos"),
            ),
        ])
    else:
        # Otros tipos de usuario (sin opciones de menú)
        pass

    return Column(
        controls=controls
    )
