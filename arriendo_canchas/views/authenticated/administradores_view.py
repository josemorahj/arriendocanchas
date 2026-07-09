# arriendo_canchas/views/authenticated/administradores_view.py

from flet import Column, Row, Text, ElevatedButton, TextField, DataTable, DataColumn, DataRow, DataCell, IconButton, icons, AlertDialog, TextButton
from services.database_service import DatabaseService
from security.passwords import pwd_context

def AdministradoresView(page, user_vm):
    db_service = DatabaseService()
    cursor = db_service.cursor

    # Función para obtener administradores
    def fetch_administradores():
        cursor.execute("SELECT id_usuario, nombre, correo FROM usuarios WHERE tipo_cuenta = 'Administrador'")
        administradores = cursor.fetchall()
        return [{'id_usuario': a[0], 'nombre': a[1], 'correo': a[2]} for a in administradores]

    admin_list = fetch_administradores()

    data_table = DataTable(
        columns=[
            DataColumn(Text("ID")),
            DataColumn(Text("Nombre")),
            DataColumn(Text("Correo")),
            DataColumn(Text("Acciones")),
        ],
        rows=[]
    )

    def create_data_row(admin):
        return DataRow(
            cells=[
                DataCell(Text(str(admin['id_usuario']))),
                DataCell(Text(admin['nombre'])),
                DataCell(Text(admin['correo'])),
                DataCell(
                    Row(
                        [
                            IconButton(icon=icons.EDIT, tooltip="Editar", on_click=lambda e, admin=admin: open_edit_dialog(admin)),
                            IconButton(icon=icons.DELETE, tooltip="Eliminar", on_click=lambda e, admin=admin: open_delete_dialog(admin)),
                        ]
                    )
                )
            ]
        )

    def refresh_data():
        admin_list = fetch_administradores()
        data_table.rows = [create_data_row(admin) for admin in admin_list]
        page.update()

    data_table.rows = [create_data_row(admin) for admin in admin_list]

    # Funciones para agregar, editar y eliminar

    def open_add_dialog(e):
        nombre_field = TextField(label="Nombre")
        correo_field = TextField(label="Correo")
        contrasena_field = TextField(label="Contraseña", password=True)

        def save_new_admin(e):
            nombre = nombre_field.value
            correo = correo_field.value
            contrasena = contrasena_field.value

                        # Insertar en la base de datos
            try:
                hashed_password = pwd_context.hash(contrasena)
                query = """
                INSERT INTO usuarios (nombre, correo, contrasena, tipo_cuenta)
                VALUES (%s, %s, %s, 'Administrador')
                """
                cursor.execute(query, (nombre, correo, hashed_password))
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                print(f"Error al agregar administrador: {ex}")
                page.dialog.open = False

        page.dialog = AlertDialog(
            title=Text("Agregar Administrador"),
            content=Column([
                nombre_field,
                correo_field,
                contrasena_field,
            ]),
            actions=[
                TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Guardar", on_click=save_new_admin),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    def open_edit_dialog(admin):
        nombre_field = TextField(label="Nombre", value=admin['nombre'])
        correo_field = TextField(label="Correo", value=admin['correo'])

        def save_edit_admin(e):
            nombre = nombre_field.value
            correo = correo_field.value
            admin_id = admin['id_usuario']

            try:
                query = """
                UPDATE usuarios SET nombre = %s, correo = %s WHERE id_usuario = %s
                """
                cursor.execute(query, (nombre, correo, admin_id))
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                print(f"Error al editar administrador: {ex}")
                page.dialog.open = False

        page.dialog = AlertDialog(
            title=Text("Editar Administrador"),
            content=Column([
                nombre_field,
                correo_field,
            ]),
            actions=[
                TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                TextButton("Guardar", on_click=save_edit_admin),
            ],
            actions_alignment="end",
        )
        page.dialog.open = True
        page.update()

    def open_delete_dialog(admin):
        def confirm_delete(e):
            admin_id = admin['id_usuario']
            try:
                query = "DELETE FROM usuarios WHERE id_usuario = %s"
                cursor.execute(query, (admin_id,))
                db_service.connection.commit()
                page.dialog.open = False
                refresh_data()
            except Exception as ex:
                print(f"Error al eliminar administrador: {ex}")
                page.dialog.open = False

        page.dialog = AlertDialog(
            title=Text("Eliminar Administrador"),
            content=Text(f"¿Está seguro de eliminar al administrador {admin['nombre']}?"),
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
                    Text("Gestionar Administradores", size=24, weight="bold"),
                    ElevatedButton("Agregar Administrador", on_click=open_add_dialog),
                ],
                alignment="spaceBetween",
            ),
            data_table,
        ]
    )
