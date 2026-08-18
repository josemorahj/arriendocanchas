import traceback

from flet import (
    AlertDialog,
    Column,
    DataCell,
    DataColumn,
    DataRow,
    DataTable,
    ElevatedButton,
    Row,
    Text,
    TextButton,
    TextField,
)

from models.cancha_model import CanchaModel
from models.complejo_model import ComplejoModel
from models.reserva_model import ReservaModel
from services.database_service import DatabaseService


def BuscarComplejosView(page, user_vm):
    complejo_model = ComplejoModel()
    db_service = DatabaseService()
    cancha_model = CanchaModel(db_service)
    reserva_model = ReservaModel(db_service)

    id_usuario_actual = user_vm.get_user()["id_usuario"]

    # Campo de búsqueda
    search_field = TextField(label="Buscar Complejo Deportivo")

    complejos_table = DataTable(
        columns=[
            DataColumn(Text("Nombre Complejo")),
            DataColumn(Text("Dirección")),
            DataColumn(Text("Acciones")),
        ],
        rows=[],
    )

    def cerrar_dialogo(e):
        page.dialog.open = False
        page.update()

    def buscar_complejos(e):
        termino = search_field.value

        if not termino or not termino.strip():
            page.dialog = AlertDialog(
                title=Text("Campo Vacío"),
                content=Text(
                    "Por favor, ingrese un término de búsqueda"
                ),
                actions=[
                    TextButton(
                        "OK",
                        on_click=cerrar_dialogo,
                    ),
                ],
                actions_alignment="end",
            )
            page.dialog.open = True
            page.update()
            return

        complejos_list = complejo_model.fetch_complejos_by_name(
            termino
        )

        complejos_table.rows = [
            create_complejo_row(complejo)
            for complejo in complejos_list
        ]

        page.update()

    def create_complejo_row(complejo):
        return DataRow(
            cells=[
                DataCell(
                    Text(complejo["nombre_complejo"])
                ),
                DataCell(
                    Text(complejo["direccion"])
                ),
                DataCell(
                    ElevatedButton(
                        "Ver Canchas",
                        on_click=lambda e, complejo=complejo: (
                            ver_canchas(complejo)
                        ),
                    )
                ),
            ]
        )

    def ver_canchas(complejo):
        nombre_complejo = complejo["nombre_complejo"]

        canchas_list = (
            cancha_model.fetch_canchas_by_complejo(
                complejo["id_complejo"]
            )
        )

        canchas_table = DataTable(
            columns=[
                DataColumn(Text("Nombre Cancha")),
                DataColumn(Text("Tipo Cancha")),
                DataColumn(Text("Acciones")),
            ],
            rows=[
                DataRow(
                    cells=[
                        DataCell(
                            Text(cancha["nombre_cancha"])
                        ),
                        DataCell(
                            Text(cancha["tipo_cancha"])
                        ),
                        DataCell(
                            ElevatedButton(
                                "Ver Disponibilidad",
                                on_click=(
                                    lambda e,
                                    cancha=cancha,
                                    nombre_complejo=nombre_complejo:
                                    ver_disponibilidad(
                                        cancha,
                                        nombre_complejo,
                                    )
                                ),
                            )
                        ),
                    ]
                )
                for cancha in canchas_list
            ],
        )

        page.dialog = AlertDialog(
            title=Text(
                f"Canchas en "
                f"{complejo['nombre_complejo']}"
            ),
            content=canchas_table,
            actions=[
                TextButton(
                    "Cerrar",
                    on_click=cerrar_dialogo,
                ),
            ],
            actions_alignment="end",
        )

        page.dialog.open = True
        page.update()

    def ver_disponibilidad(
        cancha,
        nombre_complejo=None,
    ):
        disponibilidad_list = (
            cancha_model.fetch_disponibilidad(
                cancha["id_cancha"]
            )
        )

        # Enriquecer cada disponibilidad sin nueva consulta.
        for disponibilidad in disponibilidad_list:
            disponibilidad["id_cancha"] = (
                cancha["id_cancha"]
            )
            disponibilidad["nombre_cancha"] = (
                cancha["nombre_cancha"]
            )
            disponibilidad["nombre_complejo"] = (
                nombre_complejo or ""
            )

        disponibilidad_table = DataTable(
            columns=[
                DataColumn(Text("Fecha")),
                DataColumn(Text("Hora Inicio")),
                DataColumn(Text("Hora Fin")),
                DataColumn(Text("Acciones")),
            ],
            rows=[
                DataRow(
                    cells=[
                        DataCell(
                            Text(str(disponibilidad["fecha"]))
                        ),
                        DataCell(
                            Text(
                                str(
                                    disponibilidad[
                                        "hora_inicio"
                                    ]
                                )
                            )
                        ),
                        DataCell(
                            Text(
                                str(
                                    disponibilidad[
                                        "hora_fin"
                                    ]
                                )
                            )
                        ),
                        DataCell(
                            ElevatedButton(
                                "Reservar",
                                on_click=(
                                    lambda e,
                                    disponibilidad=disponibilidad,
                                    cancha=cancha:
                                    reservar_cancha(
                                        disponibilidad,
                                        cancha,
                                    )
                                ),
                            )
                        ),
                    ]
                )
                for disponibilidad in disponibilidad_list
            ],
        )

        page.dialog = AlertDialog(
            title=Text(
                f"Disponibilidad de "
                f"{cancha['nombre_cancha']}"
            ),
            content=disponibilidad_table,
            actions=[
                TextButton(
                    "Cerrar",
                    on_click=cerrar_dialogo,
                ),
            ],
            actions_alignment="end",
        )

        page.dialog.open = True
        page.update()

    def reservar_cancha(disponibilidad, cancha):
        id_usuario = id_usuario_actual
        id_cancha = disponibilidad["id_cancha"]
        fecha_reserva = disponibilidad["fecha"]
        hora_inicio = disponibilidad["hora_inicio"]
        hora_fin = disponibilidad["hora_fin"]
        id_disponibilidad = (
            disponibilidad["id_disponibilidad"]
        )
        nombre_cancha = disponibilidad["nombre_cancha"]
        nombre_complejo = disponibilidad.get(
            "nombre_complejo",
            "",
        )

        try:
            with (
                cancha_model.db_service.transaction()
                as connection
            ):
                # Eliminar la disponibilidad y comprobar
                # cuántas filas fueron afectadas.
                filas_eliminadas = (
                    cancha_model.delete_disponibilidad(
                        id_disponibilidad,
                        connection=connection,
                    )
                )

                if filas_eliminadas == 1:
                    reserva_model.add_reserva(
                        id_usuario,
                        id_cancha,
                        fecha_reserva,
                        hora_inicio,
                        hora_fin,
                        connection=connection,
                    )

            if filas_eliminadas == 1:
                page.dialog = AlertDialog(
                    title=Text("Reserva Exitosa"),
                    content=Text(
                        f"Ha reservado la cancha "
                        f"{nombre_cancha} de "
                        f"{nombre_complejo} el "
                        f"{fecha_reserva} de "
                        f"{hora_inicio} a "
                        f"{hora_fin}"
                    ),
                    actions=[
                        TextButton(
                            "OK",
                            on_click=cerrar_dialogo,
                        ),
                    ],
                )

                page.dialog.open = True
                page.update()

            else:
                page.dialog = AlertDialog(
                    title=Text(
                        "Horario No Disponible"
                    ),
                    content=Text(
                        "El horario seleccionado ya fue "
                        "reservado o dejó de estar "
                        "disponible."
                    ),
                    actions=[
                        TextButton(
                            "OK",
                            on_click=cerrar_dialogo,
                        ),
                    ],
                )

                page.dialog.open = True
                page.update()

        except Exception as ex:
            print(
                f"Error en reservar_cancha: "
                f"{type(ex).__name__}: {ex}",
                flush=True,
            )
            traceback.print_exc()

            page.dialog = AlertDialog(
                title=Text("Error"),
                content=Text(
                    "No se pudo realizar la reserva. "
                    "Por favor, inténtelo de nuevo."
                ),
                actions=[
                    TextButton(
                        "OK",
                        on_click=cerrar_dialogo,
                    ),
                ],
            )

            page.dialog.open = True
            page.update()

    return Column(
        [
            Text(
                "Buscar Complejos Deportivos",
                size=24,
                weight="bold",
            ),
            Row(
                [
                    search_field,
                    ElevatedButton(
                        "Buscar",
                        on_click=buscar_complejos,
                    ),
                ]
            ),
            complejos_table,
        ]
    )
