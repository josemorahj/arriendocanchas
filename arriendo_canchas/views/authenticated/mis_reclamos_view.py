# views/authenticated/mis_reclamos_view.py

from flet import (
    Column, DataTable, DataColumn, DataRow, DataCell, Text, ElevatedButton, TextField, Dropdown, dropdown, AlertDialog, TextButton
)
from models.reclamo_model import ReclamoModel
from models.reserva_model import ReservaModel







def MisReclamosView(page, user_vm):
    reclamo_model = ReclamoModel()
    reserva_model = ReservaModel()
    id_usuario = user_vm.get_user()['id_usuario']
    rut_cliente = user_vm.get_user()['rut']

    reclamos_list = reclamo_model.fetch_reclamos(id_usuario)

    reclamos_table = DataTable(
        columns=[
            DataColumn(Text("Cancha")),
            DataColumn(Text("Fecha Reserva")),
            DataColumn(Text("Tipo Reclamo")),
            DataColumn(Text("Estado")),
        ],
        rows=[DataRow(
            cells=[
                DataCell(Text(r['nombre_cancha'])),
                DataCell(Text(str(r['fecha_reserva']))),
                DataCell(Text(r['tipo_reclamo'])),
                DataCell(Text(r['estado'])),
            ]
        ) for r in reclamos_list]
    )

    def open_add_reclamo_dialog(e):
        # Obtener reservas del usuario
        reservas_list = reserva_model.fetch_reservas(id_usuario)

        # Validar: usuario sin reservas
        if not reservas_list:
            page.dialog = AlertDialog(
                title=Text("Sin reservas disponibles"),
                content=Text(
                    "No tienes reservas para asociar a un reclamo. "
                    "Debes tener al menos una reserva para poder crear un reclamo."
                ),
                actions=[
                    TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                ],
                actions_alignment="end",
            )
            page.dialog.open = True
            page.update()
            return

        reserva_options = [dropdown.Option(str(r['id_reserva']), f"{r['nombre_cancha']} - {r['fecha_reserva']}") for r in reservas_list]

        reserva_dropdown = Dropdown(
            label="Reserva",
            options=reserva_options
        )
        tipo_reclamo_field = TextField(label="Tipo de Reclamo")
        error_text = Text("", color="red", size=12)

        def save_new_reclamo(e):
            # Limpiar mensaje de error previo
            error_text.value = ""

            # 1. Validar selección de reserva
            raw_reserva = reserva_dropdown.value
            if raw_reserva is None:
                error_text.value = "Debes seleccionar una reserva."
                page.update()
                return

            # 2. Conversión segura de id_reserva
            try:
                id_reserva = int(raw_reserva)
            except (TypeError, ValueError):
                error_text.value = "La reserva seleccionada no es válida."
                page.update()
                return

            # 3. Validar tipo de reclamo obligatorio (normalizado)
            tipo_reclamo = (tipo_reclamo_field.value or "").strip()
            if not tipo_reclamo:
                error_text.value = "El tipo de reclamo es obligatorio."
                page.update()
                return

            # 4. Intentar guardar el reclamo
            try:
                reclamo_model.add_reclamo(id_reserva, rut_cliente, tipo_reclamo)
                page.dialog.open = False
                # Refrescar la lista de reclamos
                reclamos_list[:] = reclamo_model.fetch_reclamos(id_usuario)
                reclamos_table.rows = [DataRow(
                    cells=[
                        DataCell(Text(r['nombre_cancha'])),
                        DataCell(Text(str(r['fecha_reserva']))),
                        DataCell(Text(r['tipo_reclamo'])),
                        DataCell(Text(r['estado'])),
                    ]
                ) for r in reclamos_list]
                page.update()
            except Exception as ex:
                print(f"Error al agregar reclamo: {ex}")
                error_text.value = "Ocurrió un error inesperado. Intenta nuevamente."
                page.update()

        page.dialog = AlertDialog(
            title=Text("Agregar Reclamo"),
            content=Column([
                reserva_dropdown,
                tipo_reclamo_field,
                error_text,
            ]),
            actions=[
                TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Guardar", on_click=save_new_reclamo),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    return Column(
        [
            Text("Mis Reclamos", size=24, weight="bold"),
            ElevatedButton("Agregar Reclamo", on_click=open_add_reclamo_dialog),
            reclamos_table,
        ]
    )
