# views/authenticated/arrendadores_view.py

from flet import Column, Row, Text, ElevatedButton, TextField, DataTable, DataColumn, DataRow, DataCell, IconButton, icons, AlertDialog, TextButton
from services.database_service import DatabaseService
from security.passwords import pwd_context

def ArrendadoresView(page, user_vm):
    db_service = DatabaseService()
    cursor = db_service.cursor

    # Función para obtener arrendadores
    def fetch_arrendadores():
        cursor.execute("SELECT id_usuario, nombre, correo FROM usuarios WHERE tipo_cuenta = 'ClienteArrendador'")
        arrendadores = cursor.fetchall()
        return [{'id_usuario': a[0], 'nombre': a[1], 'correo': a[2]} for a in arrendadores]

    arrendador_list = fetch_arrendadores()

    data_table = DataTable(
        columns=[
            DataColumn(Text("ID")),
            DataColumn(Text("Nombre")),
            DataColumn(Text("Correo")),
            DataColumn(Text("Acciones")),
        ],
        rows=[]
    )

    def create_data_row(arrendador):
        return DataRow(
            cells=[
                DataCell(Text(str(arrendador['id_usuario']))),
                DataCell(Text(arrendador['nombre'])),
                DataCell(Text(arrendador['correo'])),
                DataCell(
                    Row(
                        [
                            IconButton(icon=icons.EDIT, tooltip="Editar", on_click=lambda e, arrendador=arrendador: open_edit_dialog(arrendador)),
                            IconButton(icon=icons.DELETE, tooltip="Eliminar", on_click=lambda e, arrendador=arrendador: open_delete_dialog(arrendador)),
                        ]
                    )
                )
            ]
        )

    def refresh_data():
        arrendador_list = fetch_arrendadores()
        data_table.rows = [create_data_row(arrendador) for arrendador in arrendador_list]
        page.update()

    data_table.rows = [create_data_row(arrendador) for arrendador in arrendador_list]

        # Funciones para agregar, editar y eliminar

    def open_add_dialog(e):
        nombre_field = TextField(label="Nombre")
        correo_field = TextField(label="Correo")
        contrasena_field = TextField(label="Contraseña", password=True)

        def save_new_arrendador(e):
            nombre = nombre_field.value
            correo = correo_field.value
            contrasena = contrasena_field.value

            # Insertar en la base de datos
            try:
                hashed_password = pwd_context.hash(contrasena)
                query = """
                INSERT INTO usuarios (nombre, correo, contrasena, tipo_cuenta)
                VALUES (%s, %s, %s, 'ClienteArrendador')
                """
                cursor.execute(query, (nombre, correo, hashed_password))
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                print(f"Error al agregar arrendador: {ex}")
                page.dialog.open = False

        page.dialog = AlertDialog(
            title=Text("Agregar Arrendador"),
            content=Column([
                nombre_field,
                correo_field,
                contrasena_field,
            ]),
            actions=[
                TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Guardar", on_click=save_new_arrendador),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    def open_edit_dialog(arrendador):
        nombre_field = TextField(label="Nombre", value=arrendador['nombre'])
        correo_field = TextField(label="Correo", value=arrendador['correo'])

        def save_edit_arrendador(e):
            nombre = nombre_field.value
            correo = correo_field.value
            arrendador_id = arrendador['id_usuario']

            try:
                query = """
                UPDATE usuarios SET nombre = %s, correo = %s WHERE id_usuario = %s
                """
                cursor.execute(query, (nombre, correo, arrendador_id))
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                print(f"Error al editar arrendador: {ex}")
                page.dialog.open = False

        page.dialog = AlertDialog(
            title=Text("Editar Arrendador"),
            content=Column([
                nombre_field,
                correo_field,
            ]),
            actions=[
                TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Guardar", on_click=save_edit_arrendador),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    def open_delete_dialog(arrendador):
        def confirm_delete(e):
            arrendador_id = arrendador['id_usuario']
            try:
                query = "DELETE FROM usuarios WHERE id_usuario = %s"
                cursor.execute(query, (arrendador_id,))
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                print(f"Error al eliminar arrendador: {ex}")
                page.dialog.open = False

        page.dialog = AlertDialog(
            title=Text("Eliminar Arrendador"),
            content=Text(f"¿Está seguro de eliminar al arrendador {arrendador['nombre']}?"),
            actions=[
                TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Eliminar", on_click=confirm_delete),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    return Column(
        [
            Row(
                [
                    Text("Gestionar Arrendadores", size=24, weight="bold"),
                    ElevatedButton("Agregar Arrendador", on_click=open_add_dialog),
                ],
                alignment="spaceBetween",
            ),
            data_table,
        ]
    )
