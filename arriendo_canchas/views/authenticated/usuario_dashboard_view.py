# views/authenticated/usuario_dashboard_view.py

from flet import (
    Column, Text, ElevatedButton
)


def UsuarioDashboardView(page, user_vm):
    user = user_vm.get_user()

    def ir_mis_datos(e):
        page.go("/mis_datos")

    def ir_buscar_complejos(e):
        page.go("/buscar_complejos")

    def ir_mis_reservas(e):
        page.go("/mis_reservas")

    def ir_mis_reclamos(e):
        page.go("/mis_reclamos")

    return Column(
        [
            Text(f"Bienvenido, {user['nombre']}", size=24, weight="bold"),
            Text(
                "Has iniciado sesión como Usuario. "
                "Selecciona una opción para comenzar."
            ),
            ElevatedButton("Mis Datos", on_click=ir_mis_datos),
            ElevatedButton("Buscar Complejos", on_click=ir_buscar_complejos),
            ElevatedButton("Mis Reservas", on_click=ir_mis_reservas),
            ElevatedButton("Mis Reclamos", on_click=ir_mis_reclamos),
        ]
    )
