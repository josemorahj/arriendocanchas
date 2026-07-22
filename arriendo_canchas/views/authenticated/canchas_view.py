from flet import (
    Column, Row, Text, ElevatedButton, TextField, DataTable, DataColumn,
    DataRow, DataCell, IconButton, icons, AlertDialog, TextButton, Dropdown, dropdown
)
from datetime import datetime
from services.database_service import DatabaseService
from models.cancha_model import CanchaModel

def CanchasView(page, user_vm):
    db_service = DatabaseService()
    cursor = db_service.cursor
    cancha_model = CanchaModel()

    # Obtener el id del usuario actual
    user = user_vm.get_user()
    user_id = user['id_usuario']

    # Función para obtener canchas del arrendador
    def fetch_canchas():
        query = """
        SELECT c.id_cancha, c.nombre_cancha, c.tipo_cancha, co.nombre_complejo
        FROM Canchas c
        JOIN ComplejosDeportivos co ON c.id_complejo = co.id_complejo
        WHERE co.id_usuario = %s
        """
        cursor.execute(query, (user_id,))
        canchas = cursor.fetchall()
        return [{'id_cancha': c[0], 'nombre_cancha': c[1], 'tipo_cancha': c[2], 'complejo_nombre': c[3]} for c in canchas]

    cancha_list = fetch_canchas()

    data_table = DataTable(
        columns=[
            DataColumn(Text("ID")),
            DataColumn(Text("Nombre Cancha")),
            DataColumn(Text("Tipo Cancha")),
            DataColumn(Text("Complejo")),
            DataColumn(Text("Acciones")),
        ],
        rows=[]
    )

    def create_data_row(cancha):
        return DataRow(
            cells=[
                DataCell(Text(str(cancha['id_cancha']))),
                DataCell(Text(cancha['nombre_cancha'])),
                DataCell(Text(cancha['tipo_cancha'])),
                DataCell(Text(cancha['complejo_nombre'])),
                DataCell(
                    Row(
                        [
                            IconButton(
                                icon=icons.ACCESS_TIME,
                                tooltip="Gestionar Disponibilidad",
                                on_click=lambda e, cancha=cancha: open_disponibilidad_dialog(cancha)
                            ),
                            IconButton(
                                icon=icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, cancha=cancha: open_edit_dialog(cancha)
                            ),
                            IconButton(
                                icon=icons.DELETE,
                                tooltip="Eliminar",
                                on_click=lambda e, cancha=cancha: open_delete_dialog(cancha)
                            ),
                        ]
                    )
                )
            ]
        )

    def refresh_data():
        cancha_list = fetch_canchas()
        data_table.rows = [create_data_row(cancha) for cancha in cancha_list]
        page.update()

    data_table.rows = [create_data_row(cancha) for cancha in cancha_list]

    # Obtener lista de complejos del arrendador
    def fetch_complejos():
        query = """
        SELECT id_complejo, nombre_complejo
        FROM ComplejosDeportivos
        WHERE id_usuario = %s
        """
        cursor.execute(query, (user_id,))
        complejos = cursor.fetchall()
        return [{'id_complejo': c[0], 'nombre_complejo': c[1]} for c in complejos]

    complejos_list = fetch_complejos()

    # Funciones para agregar, editar y eliminar canchas

    def open_add_dialog(e):
        nombre_field = TextField(label="Nombre Cancha")
        tipo_field = TextField(label="Tipo Cancha")
        complejo_dropdown = Dropdown(
            label="Complejo Deportivo",
            options=[dropdown.Option(str(c['id_complejo']), c['nombre_complejo']) for c in complejos_list]
        )

        def save_new_cancha(e):
            nombre = nombre_field.value
            tipo = tipo_field.value
            id_complejo = int(complejo_dropdown.value)

            # Insertar en la base de datos
            try:
                query = """
                INSERT INTO Canchas (nombre_cancha, tipo_cancha, id_complejo)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (nombre, tipo, id_complejo))
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                db_service.connection.rollback()
                print(f"Error al agregar cancha: {ex}")
                page.dialog.open = False

        page.dialog = AlertDialog(
            title=Text("Agregar Cancha"),
            content=Column([
                nombre_field,
                tipo_field,
                complejo_dropdown,
            ]),
            actions=[
                TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Guardar", on_click=save_new_cancha),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    def open_edit_dialog(cancha):
        nombre_field = TextField(label="Nombre Cancha", value=cancha['nombre_cancha'])
        tipo_field = TextField(label="Tipo Cancha", value=cancha['tipo_cancha'])
        complejo_dropdown = Dropdown(
            label="Complejo Deportivo",
            options=[dropdown.Option(str(c['id_complejo']), c['nombre_complejo']) for c in complejos_list],
            value=str(next(c['id_complejo'] for c in complejos_list if c['nombre_complejo'] == cancha['complejo_nombre']))
        )

        def save_edit_cancha(e):
            nombre = nombre_field.value
            tipo = tipo_field.value
            id_complejo = int(complejo_dropdown.value)
            cancha_id = cancha['id_cancha']

            try:
                query = """
                UPDATE Canchas
                SET nombre_cancha = %s, tipo_cancha = %s, id_complejo = %s
                WHERE id_cancha = %s
                """
                cursor.execute(query, (nombre, tipo, id_complejo, cancha_id))
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                db_service.connection.rollback()
                print(f"Error al editar cancha: {ex}")
                page.dialog.open = False

        page.dialog = AlertDialog(
            title=Text("Editar Cancha"),
            content=Column([
                nombre_field,
                tipo_field,
                complejo_dropdown,
            ]),
            actions=[
                TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Guardar", on_click=save_edit_cancha),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    def open_delete_dialog(cancha):
        def confirm_delete(e):
            cancha_id = cancha['id_cancha']
            try:
                query = "DELETE FROM Canchas WHERE id_cancha = %s"
                cursor.execute(query, (cancha_id,))
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                db_service.connection.rollback()
                print(f"Error al eliminar cancha: {ex}")
                page.dialog.open = False

        page.dialog = AlertDialog(
            title=Text("Eliminar Cancha"),
            content=Text(f"¿Está seguro de eliminar la cancha {cancha['nombre_cancha']}?"),
            actions=[
                TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Eliminar", on_click=confirm_delete),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    # Funciones para gestionar disponibilidad

    def open_disponibilidad_dialog(cancha):
        disponibilidad_list = cancha_model.fetch_disponibilidad(cancha['id_cancha'])

        disponibilidad_table = DataTable(
            columns=[
                DataColumn(Text("Fecha")),
                DataColumn(Text("Hora Inicio")),
                DataColumn(Text("Hora Fin")),
                DataColumn(Text("Acciones")),
            ],
            rows=[]
        )

        def create_disponibilidad_row(disponibilidad):
            return DataRow(
                cells=[
                    DataCell(Text(str(disponibilidad['fecha']))),
                    DataCell(Text(str(disponibilidad['hora_inicio']))),
                    DataCell(Text(str(disponibilidad['hora_fin']))),
                    DataCell(
                        Row(
                            [
                                IconButton(
                                    icon=icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, disponibilidad=disponibilidad: open_edit_disponibilidad_dialog(disponibilidad)
                                ),
                                IconButton(
                                    icon=icons.DELETE,
                                    tooltip="Eliminar",
                                    on_click=lambda e, disponibilidad=disponibilidad: open_delete_disponibilidad_dialog(disponibilidad)
                                ),
                            ]
                        )
                    )
                ]
            )

        def refresh_disponibilidad():
            disponibilidad_list = cancha_model.fetch_disponibilidad(cancha['id_cancha'])
            disponibilidad_table.rows = [create_disponibilidad_row(d) for d in disponibilidad_list]
            page.update()

        disponibilidad_table.rows = [create_disponibilidad_row(d) for d in disponibilidad_list]

        # Funciones para agregar, editar y eliminar disponibilidad
        def open_add_disponibilidad_dialog(e):
            fecha_field = TextField(label="Fecha (YYYY-MM-DD)")
            hora_inicio_field = TextField(label="Hora Inicio (HH:MM)")
            hora_fin_field = TextField(label="Hora Fin (HH:MM)")

            def save_new_disponibilidad(e):
                fecha = fecha_field.value
                hora_inicio = hora_inicio_field.value
                hora_fin = hora_fin_field.value

                # Validaciones
                if not fecha or not hora_inicio or not hora_fin:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("Todos los campos son obligatorios."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                try:
                    datetime.strptime(fecha, "%Y-%m-%d")
                except ValueError:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("La fecha debe tener formato YYYY-MM-DD."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                try:
                    hora_inicio_dt = datetime.strptime(hora_inicio, "%H:%M")
                except ValueError:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("La hora de inicio debe tener formato HH:MM."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                try:
                    hora_fin_dt = datetime.strptime(hora_fin, "%H:%M")
                except ValueError:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("La hora de fin debe tener formato HH:MM."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                if hora_fin_dt <= hora_inicio_dt:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("La hora de fin debe ser mayor a la hora de inicio."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                try:
                    cancha_model.add_disponibilidad(cancha['id_cancha'], fecha, hora_inicio, hora_fin)
                    page.dialog.open = False
                    refresh_disponibilidad()
                except Exception as ex:
                    print(f"Error al agregar disponibilidad: {ex}")
                    page.dialog = AlertDialog(
                        title=Text("Error"),
                        content=Text("Ocurrió un error al agregar la disponibilidad."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()

            page.dialog = AlertDialog(
                title=Text("Agregar Disponibilidad"),
                content=Column([
                    fecha_field,
                    hora_inicio_field,
                    hora_fin_field,
                ]),
                actions=[
                    TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                    TextButton("Guardar", on_click=save_new_disponibilidad),
                ],
                actions_alignment="end",
            )
            page.dialog.open = True
            page.update()

        def open_edit_disponibilidad_dialog(disponibilidad):
            fecha_field = TextField(label="Fecha (YYYY-MM-DD)", value=str(disponibilidad['fecha']))
            hora_inicio_field = TextField(label="Hora Inicio (HH:MM)", value=str(disponibilidad['hora_inicio']))
            hora_fin_field = TextField(label="Hora Fin (HH:MM)", value=str(disponibilidad['hora_fin']))

            def save_edit_disponibilidad(e):
                fecha = fecha_field.value
                hora_inicio = hora_inicio_field.value
                hora_fin = hora_fin_field.value
                id_disponibilidad = disponibilidad['id_disponibilidad']

                # Validaciones
                if not fecha or not hora_inicio or not hora_fin:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("Todos los campos son obligatorios."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                try:
                    datetime.strptime(fecha, "%Y-%m-%d")
                except ValueError:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("La fecha debe tener formato YYYY-MM-DD."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                try:
                    hora_inicio_dt = datetime.strptime(hora_inicio, "%H:%M")
                except ValueError:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("La hora de inicio debe tener formato HH:MM."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                try:
                    hora_fin_dt = datetime.strptime(hora_fin, "%H:%M")
                except ValueError:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("La hora de fin debe tener formato HH:MM."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                if hora_fin_dt <= hora_inicio_dt:
                    page.dialog = AlertDialog(
                        title=Text("Error de validación"),
                        content=Text("La hora de fin debe ser mayor a la hora de inicio."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()
                    return

                try:
                    cancha_model.update_disponibilidad(id_disponibilidad, fecha, hora_inicio, hora_fin)
                    page.dialog.open = False
                    refresh_disponibilidad()
                except Exception as ex:
                    print(f"Error al editar disponibilidad: {ex}")
                    page.dialog = AlertDialog(
                        title=Text("Error"),
                        content=Text("Ocurrió un error al editar la disponibilidad."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()

            page.dialog = AlertDialog(
                title=Text("Editar Disponibilidad"),
                content=Column([
                    fecha_field,
                    hora_inicio_field,
                    hora_fin_field,
                ]),
                actions=[
                    TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                    TextButton("Guardar", on_click=save_edit_disponibilidad),
                ],
                actions_alignment="end",
            )
            page.dialog.open = True
            page.update()

        def open_delete_disponibilidad_dialog(disponibilidad):
            def confirm_delete(e):
                id_disponibilidad = disponibilidad['id_disponibilidad']
                try:
                    filas_eliminadas = cancha_model.delete_disponibilidad(id_disponibilidad)
                    cancha_model.db_service.connection.commit()

                    if filas_eliminadas == 1:
                        page.dialog.open = False
                        refresh_disponibilidad()
                    else:
                        page.dialog = AlertDialog(
                            title=Text("Error"),
                            content=Text("La disponibilidad ya no existe o fue eliminada."),
                            actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                            actions_alignment="end",
                        )
                        page.dialog.open = True
                        page.update()
                except Exception as ex:
                    cancha_model.db_service.connection.rollback()
                    print(f"Error al eliminar disponibilidad: {ex}")
                    page.dialog = AlertDialog(
                        title=Text("Error"),
                        content=Text("Ocurrió un error al eliminar la disponibilidad."),
                        actions=[TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False))],
                        actions_alignment="end",
                    )
                    page.dialog.open = True
                    page.update()

            page.dialog = AlertDialog(
                title=Text("Eliminar Disponibilidad"),
                content=Text(f"¿Está seguro de eliminar la disponibilidad del {disponibilidad['fecha']} de {disponibilidad['hora_inicio']} a {disponibilidad['hora_fin']}?"),
                actions=[
                    TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                    TextButton("Eliminar", on_click=confirm_delete),
                ],
                actions_alignment="end",
            )
            page.dialog.open = True
            page.update()

        # Dialog para gestionar disponibilidad
        page.dialog = AlertDialog(
            title=Text(f"Disponibilidad para {cancha['nombre_cancha']}"),
            content=Column([
                Row(
                    [
                        ElevatedButton("Agregar Disponibilidad", on_click=open_add_disponibilidad_dialog),
                    ],
                    alignment="start",
                ),
                disponibilidad_table,
            ]),
            actions=[
                TextButton("Cerrar", on_click=lambda e: setattr(page.dialog, 'open', False)),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    return Column(
        [
            Row(
                [
                    Text("Gestionar Canchas", size=24, weight="bold"),
                    ElevatedButton("Agregar Cancha", on_click=open_add_dialog),
                ],
                alignment="spaceBetween",
            ),
            data_table,
        ]
    )
