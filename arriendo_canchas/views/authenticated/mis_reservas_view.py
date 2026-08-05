# views/authenticated/mis_reservas_view.py

from flet import (
    Column, DataTable, DataColumn, DataRow, DataCell, Text, IconButton, icons, AlertDialog, TextButton
)
from models.reserva_model import ReservaModel

def MisReservasView(page, user_vm):
    reserva_model = ReservaModel()
    id_usuario = user_vm.get_user()['id_usuario']

    reservas_list = reserva_model.fetch_reservas(id_usuario)

    reservas_table = DataTable(
        columns=[
            DataColumn(Text("Cancha")),
            DataColumn(Text("Fecha")),
            DataColumn(Text("Hora Inicio")),
            DataColumn(Text("Hora Fin")),
            DataColumn(Text("Estado")),
            DataColumn(Text("Acciones")),
        ],
        rows=[DataRow(
            cells=[
                DataCell(Text(r['nombre_cancha'])),
                DataCell(Text(str(r['fecha_reserva']))),
                DataCell(Text(str(r['hora_inicio']))),
                DataCell(Text(str(r['hora_fin']))),
                DataCell(Text(r['estado'])),
                DataCell(
                    IconButton(icon=icons.DELETE, tooltip="Cancelar Reserva", on_click=lambda e, reserva=r: cancelar_reserva(reserva))
                ),
            ]
        ) for r in reservas_list]
    )

    def cancelar_reserva(reserva):
        def confirm_cancel(e):
            id_reserva = reserva['id_reserva']
            try:
                # Actualizar el estado de la reserva a 'Cancelada'
                with reserva_model.db_service.transaction() as connection:
                    reserva_model.update_reserva_estado(
                        id_reserva,
                        'Cancelada',
                        connection=connection,
                    )
                page.dialog.open = False
                page.update()
                # Refrescar la lista de reservas
                reservas_list[:] = reserva_model.fetch_reservas(id_usuario)
                reservas_table.rows = [DataRow(
                    cells=[
                        DataCell(Text(r['nombre_cancha'])),
                        DataCell(Text(str(r['fecha_reserva']))),
                        DataCell(Text(str(r['hora_inicio']))),
                        DataCell(Text(str(r['hora_fin']))),
                        DataCell(Text(r['estado'])),
                        DataCell(
                            IconButton(icon=icons.DELETE, tooltip="Cancelar Reserva", on_click=lambda e, reserva=r: cancelar_reserva(reserva))
                        ),
                    ]
                ) for r in reservas_list]
                page.update()
            except Exception as ex:
                print(f"Error al cancelar reserva: {ex}")
                page.dialog.open = False
                page.update()

        page.dialog = AlertDialog(
            title=Text("Cancelar Reserva"),
            content=Text(f"¿Está seguro de cancelar la reserva de la cancha {reserva['nombre_cancha']} el {reserva['fecha_reserva']}?"),
            actions=[
                TextButton("No", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Sí", on_click=confirm_cancel),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    return Column(
        [
            Text("Mis Reservas", size=24, weight="bold"),
            reservas_table,
        ]
    )
