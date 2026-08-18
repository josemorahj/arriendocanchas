# models/reclamo_model.py

from services.database_service import DatabaseService


class ReclamoModel:
    def __init__(self):
        self.db_service = DatabaseService()
        self.cursor = self.db_service.cursor

    def fetch_all_reclamos(self):
        query = """
        SELECT r.id_reclamo, u.nombre, c.nombre_cancha,
               res.fecha_reserva, r.tipo_reclamo, r.estado
        FROM Reclamos r
        JOIN Reservas res ON r.id_reserva = res.id_reserva
        JOIN Usuarios u ON res.id_usuario = u.id_usuario
        JOIN Canchas c ON res.id_cancha = c.id_cancha
        ORDER BY r.id_reclamo DESC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [
            {
                'id_reclamo': row[0],
                'nombre_usuario': row[1],
                'nombre_cancha': row[2],
                'fecha_reserva': row[3],
                'tipo_reclamo': row[4],
                'estado': row[5],
            }
            for row in rows
        ]

    def update_estado_reclamo(self, id_reclamo, nuevo_estado):
        query = "UPDATE Reclamos SET estado = %s WHERE id_reclamo = %s"
        self.cursor.execute(query, (nuevo_estado, id_reclamo))
        self.db_service.connection.commit()

    def fetch_reclamos(self, id_usuario):
        query = """
        SELECT r.id_reclamo, r.tipo_reclamo, r.estado, res.fecha_reserva, c.nombre_cancha
        FROM Reclamos r
        JOIN Reservas res ON r.id_reserva = res.id_reserva
        JOIN Canchas c ON res.id_cancha = c.id_cancha
        WHERE res.id_usuario = %s
        """
        self.cursor.execute(query, (id_usuario,))
        reclamos = self.cursor.fetchall()
        return [{
            "id_reclamo": r[0],
            "tipo_reclamo": r[1],
            "estado": r[2],
            "fecha_reserva": r[3],
            "nombre_cancha": r[4]
        } for r in reclamos]

    def add_reclamo(self, id_reserva, rut_cliente, tipo_reclamo):
        query = """
        INSERT INTO Reclamos (id_reserva, rut_cliente, tipo_reclamo)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (id_reserva, rut_cliente, tipo_reclamo))
        self.db_service.connection.commit()
