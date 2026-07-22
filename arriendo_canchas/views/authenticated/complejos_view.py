from flet import (
    Column,
    Row,
    Text,
    ElevatedButton,
    TextField,
    DataTable,
    DataColumn,
    DataRow,
    DataCell,
    IconButton,
    icons,
    AlertDialog,
    TextButton,
)
from services.database_service import DatabaseService


def ComplejosView(page, user_vm):
    db_service = DatabaseService()
    cursor = db_service.cursor

    # Obtener el id del usuario actual
    user = user_vm.get_user()
    user_id = user["id_usuario"]

    # Función para obtener complejos deportivos del arrendador
    def fetch_complejos():
        query = """
        SELECT id_complejo, nombre_complejo, direccion
        FROM ComplejosDeportivos
        WHERE id_usuario = %s
        """
        cursor.execute(query, (user_id,))
        complejos = cursor.fetchall()

        return [
            {
                "id_complejo": complejo[0],
                "nombre_complejo": complejo[1],
                "direccion": complejo[2],
            }
            for complejo in complejos
        ]

    complejo_list = fetch_complejos()

    data_table = DataTable(
        columns=[
            DataColumn(Text("ID")),
            DataColumn(Text("Nombre Complejo")),
            DataColumn(Text("Dirección")),
            DataColumn(Text("Acciones")),
        ],
        rows=[],
    )

    def create_data_row(complejo):
        return DataRow(
            cells=[
                DataCell(Text(str(complejo["id_complejo"]))),
                DataCell(Text(complejo["nombre_complejo"])),
                DataCell(Text(complejo["direccion"])),
                DataCell(
                    Row(
                        [
                            IconButton(
                                icon=icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, complejo=complejo: open_edit_dialog(
                                    complejo
                                ),
                            ),
                            IconButton(
                                icon=icons.DELETE,
                                tooltip="Eliminar",
                                on_click=lambda e, complejo=complejo: open_delete_dialog(
                                    complejo
                                ),
                            ),
                        ]
                    )
                ),
            ]
        )

    def refresh_data():
        complejos = fetch_complejos()
        data_table.rows = [
            create_data_row(complejo)
            for complejo in complejos
        ]
        page.update()

    data_table.rows = [
        create_data_row(complejo)
        for complejo in complejo_list
    ]

    def open_add_dialog(e):
        nombre_field = TextField(label="Nombre Complejo")
        direccion_field = TextField(label="Dirección")

        def save_new_complejo(e):
            nombre = nombre_field.value
            direccion = direccion_field.value

            try:
                query = """
                INSERT INTO ComplejosDeportivos (
                    nombre_complejo,
                    direccion,
                    id_usuario
                )
                VALUES (%s, %s, %s)
                """
                cursor.execute(
                    query,
                    (nombre, direccion, user_id),
                )
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                db_service.connection.rollback()
                print(f"Error al agregar complejo: {ex}")
                page.dialog.open = False
                page.update()

        page.dialog = AlertDialog(
            title=Text("Agregar Complejo Deportivo"),
            content=Column(
                [
                    nombre_field,
                    direccion_field,
                ]
            ),
            actions=[
                TextButton(
                    "Cancelar",
                    on_click=lambda e: setattr(
                        page.dialog,
                        "open",
                        False,
                    ),
                ),
                TextButton(
                    "Guardar",
                    on_click=save_new_complejo,
                ),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    def open_edit_dialog(complejo):
        nombre_field = TextField(
            label="Nombre Complejo",
            value=complejo["nombre_complejo"],
        )
        direccion_field = TextField(
            label="Dirección",
            value=complejo["direccion"],
        )

        def save_edit_complejo(e):
            nombre = nombre_field.value
            direccion = direccion_field.value
            complejo_id = complejo["id_complejo"]

            try:
                query = """
                UPDATE ComplejosDeportivos
                SET nombre_complejo = %s,
                    direccion = %s
                WHERE id_complejo = %s
                """
                cursor.execute(
                    query,
                    (nombre, direccion, complejo_id),
                )
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                db_service.connection.rollback()
                print(f"Error al editar complejo: {ex}")
                page.dialog.open = False
                page.update()

        page.dialog = AlertDialog(
            title=Text("Editar Complejo Deportivo"),
            content=Column(
                [
                    nombre_field,
                    direccion_field,
                ]
            ),
            actions=[
                TextButton(
                    "Cancelar",
                    on_click=lambda e: setattr(
                        page.dialog,
                        "open",
                        False,
                    ),
                ),
                TextButton(
                    "Guardar",
                    on_click=save_edit_complejo,
                ),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    def open_delete_dialog(complejo):
        def confirm_delete(e):
            complejo_id = complejo["id_complejo"]

            try:
                query = """
                DELETE FROM ComplejosDeportivos
                WHERE id_complejo = %s
                """
                cursor.execute(
                    query,
                    (complejo_id,),
                )
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                db_service.connection.rollback()
                print(f"Error al eliminar complejo: {ex}")
                page.dialog.open = False
                page.update()

        page.dialog = AlertDialog(
            title=Text("Eliminar Complejo Deportivo"),
            content=Text(
                "¿Está seguro de eliminar el complejo "
                f"{complejo['nombre_complejo']}?"
            ),
            actions=[
                TextButton(
                    "Cancelar",
                    on_click=lambda e: setattr(
                        page.dialog,
                        "open",
                        False,
                    ),
                ),
                TextButton(
                    "Eliminar",
                    on_click=confirm_delete,
                ),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    return Column(
        [
            Row(
                [
                    Text(
                        "Gestionar Complejos Deportivos",
                        size=24,
                        weight="bold",
                    ),
                    ElevatedButton(
                        "Agregar Complejo",
                        on_click=open_add_dialog,
                    ),
                ],
                alignment="spaceBetween",
            ),
            data_table,
        ]
    )
