# views/authenticated/gestion_reclamos_view.py

from flet import (
    Column, DataTable, DataColumn, DataRow, DataCell, Text, ElevatedButton, Dropdown, dropdown
)
from models.reclamo_model import ReclamoModel

# Valores controlados de estado. La columna admite texto libre a nivel de
# schema, pero la lógica de esta vista solo acepta estos cuatro valores.
ESTADOS_VALIDOS = ["Pendiente", "En revisión", "Resuelto", "Rechazado"]


def GestionReclamosView(page, user_vm):
    reclamo_model_instance = ReclamoModel()

    reclamos_list = reclamo_model_instance.fetch_all_reclamos()
    feedback_text = Text("", color="red", size=12)

    def build_rows():
        rows = []
        for r in reclamos_list:
            estado_dropdown = Dropdown(
                width=160,
                value=r['estado'] if r['estado'] in ESTADOS_VALIDOS else None,
                options=[dropdown.Option(estado) for estado in ESTADOS_VALIDOS],
            )

            def make_handler(id_reclamo, dd):
                def handler(e):
                    guardar_estado(id_reclamo, dd)
                return handler

            rows.append(DataRow(
                cells=[
                    DataCell(Text(r['nombre_usuario'])),
                    DataCell(Text(r['nombre_cancha'])),
                    DataCell(Text(str(r['fecha_reserva']))),
                    DataCell(Text(r['tipo_reclamo'])),
                    DataCell(estado_dropdown),
                    DataCell(ElevatedButton("Actualizar", on_click=make_handler(r['id_reclamo'], estado_dropdown))),
                ]
            ))
        return rows

    reclamos_table = DataTable(
        columns=[
            DataColumn(Text("Usuario")),
            DataColumn(Text("Cancha")),
            DataColumn(Text("Fecha Reserva")),
            DataColumn(Text("Tipo Reclamo")),
            DataColumn(Text("Estado")),
            DataColumn(Text("")),
        ],
        rows=build_rows(),
    )

    def guardar_estado(id_reclamo, estado_dropdown):
        feedback_text.value = ""
        nuevo_estado = estado_dropdown.value

        # Validar contra la lista controlada, aunque la columna admita texto libre.
        if nuevo_estado not in ESTADOS_VALIDOS:
            feedback_text.value = "Estado no válido."
            page.update()
            return

        try:
            reclamo_model_instance.update_estado_reclamo(id_reclamo, nuevo_estado)
            # Refrescar datos y tabla
            reclamos_list[:] = reclamo_model_instance.fetch_all_reclamos()
            reclamos_table.rows = build_rows()
            feedback_text.value = "Estado actualizado correctamente."
            page.update()
        except Exception as ex:
            print(f"Error al actualizar estado del reclamo: {ex}")
            feedback_text.value = "Ocurrió un error inesperado. Intenta nuevamente."
            page.update()

    return Column(
        [
            Text("Gestión de Reclamos", size=24, weight="bold"),
            reclamos_table,
            feedback_text,
        ]
    )
