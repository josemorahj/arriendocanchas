# views/authenticated/acceso_denegado_view.py

from flet import (
    Column, Text, ElevatedButton
)


def AccesoDenegadoView(page, user_vm):
    def volver_dashboard(e):
        page.go("/dashboard")

    return Column(
        [
            Text("Acceso denegado", size=24, weight="bold"),
            Text(
                "No tienes los permisos necesarios para acceder a esta página. "
                "Si crees que esto es un error, contacta al administrador del sistema."
            ),
            ElevatedButton("Volver al Dashboard", on_click=volver_dashboard),
        ]
    )
