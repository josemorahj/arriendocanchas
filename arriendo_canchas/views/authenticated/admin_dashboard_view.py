# views/authenticated/admin_dashboard_view.py


from flet import (
    Column, Text, ElevatedButton
)


def AdminDashboardView(page, user_vm):
    user = user_vm.get_user()

    def ir_mis_complejos(e):
        page.go("/mis_complejos")

    def ir_mis_canchas(e):
        page.go("/mis_canchas")

    def ir_gestion_reclamos(e):
        page.go("/gestion_reclamos")

    return Column(
        [
            Text(f"Bienvenido, {user['nombre']}", size=24, weight="bold"),
            Text(
                "Has iniciado sesión como Administrador. "
                "Desde aquí puedes gestionar los recursos del sistema."
            ),
            ElevatedButton("Mis Complejos", on_click=ir_mis_complejos),
            ElevatedButton("Mis Canchas", on_click=ir_mis_canchas),
            ElevatedButton("Gestionar Reclamos", on_click=ir_gestion_reclamos),
        ]
    )
