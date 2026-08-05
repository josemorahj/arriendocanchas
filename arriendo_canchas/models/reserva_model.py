# arriendo_canchas/arriendo_canchas/models/reserva_model.py

import psycopg2
from services.database_service import DatabaseService

class ReservaModel:
    def __init__(self):
        self.db_service = DatabaseService()
        self.cursor = self.db_service.cursor

    def fetch_reservas(self, id_usuario=None):
        query = """
        SELECT r.id_reserva, u.nombre, c.nombre_cancha, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.estado
        FROM Reservas r
        JOIN Usuarios u ON r.id_usuario = u.id_usuario
        JOIN Canchas c ON r.id_cancha = c.id_cancha
        """
        params = ()
        if id_usuario:
            query += " WHERE r.id_usuario = %s"
            params = (id_usuario,)
        self.cursor.execute(query, params)
        reservas = self.cursor.fetchall()
        return [{
            'id_reserva': r[0],
            'nombre_usuario': r[1],
            'nombre_cancha': r[2],
            'fecha_reserva': r[3],
            'hora_inicio': r[4],
            'hora_fin': r[5],
            'estado': r[6]
        } for r in reservas]

    def add_reserva(self, id_usuario, id_cancha, fecha_reserva, hora_inicio, hora_fin, estado='Confirmada', connection=None):
        query = """
        INSERT INTO Reservas (id_usuario, id_cancha, fecha_reserva, hora_inicio, hora_fin, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute(query, (id_usuario, id_cancha, fecha_reserva, hora_inicio, hora_fin, estado))
            return
        try:
            self.cursor.execute(query, (id_usuario, id_cancha, fecha_reserva, hora_inicio, hora_fin, estado))
            self.db_service.connection.commit()
        except Exception:
            self.db_service.connection.rollback()
            raise

    def update_reserva(self, id_reserva, fecha_reserva, estado, connection=None):
        query = """
        UPDATE Reservas 
        SET fecha_reserva = %s, estado = %s 
        WHERE id_reserva = %s
        """
        cursor = (
            connection.cursor()
            if connection is not None
            else self.cursor
        )
        if connection is not None:
            cursor.execute(query, (fecha_reserva, estado, id_reserva))
            return
        try:
            cursor.execute(query, (fecha_reserva, estado, id_reserva))
            self.db_service.connection.commit()
        except Exception:
            self.db_service.connection.rollback()
            raise

    def delete_reserva(self, id_reserva, connection=None):
        query = "DELETE FROM Reservas WHERE id_reserva = %s"
        cursor = (
            connection.cursor()
            if connection is not None
            else self.cursor
        )
        if connection is not None:
            cursor.execute(query, (id_reserva,))
            return
        try:
            cursor.execute(query, (id_reserva,))
            self.db_service.connection.commit()
        except Exception:
            self.db_service.connection.rollback()
            raise

    def update_reserva_estado(self, id_reserva, estado, connection=None):
        query = """
        UPDATE Reservas 
        SET estado = %s 
        WHERE id_reserva = %s
        """
        cursor = (
            connection.cursor()
            if connection is not None
            else self.cursor
        )
        if connection is not None:
            cursor.execute(query, (estado, id_reserva))
            return
        try:
            cursor.execute(query, (estado, id_reserva))
            self.db_service.connection.commit()
        except Exception:
            self.db_service.connection.rollback()
            raise

    def fetch_reserva_by_id(self, id_reserva):
        query = """
        SELECT r.id_reserva, u.nombre, c.nombre_cancha, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.estado
        FROM Reservas r
        JOIN Usuarios u ON r.id_usuario = u.id_usuario
        JOIN Canchas c ON r.id_cancha = c.id_cancha
        WHERE r.id_reserva = %s
        """
        self.cursor.execute(query, (id_reserva,))
        reserva = self.cursor.fetchone()
        if reserva:
            return {
                'id_reserva': reserva[0],
                'nombre_usuario': reserva[1],
                'nombre_cancha': reserva[2],
                'fecha_reserva': reserva[3],
                'hora_inicio': reserva[4],
                'hora_fin': reserva[5],
                'estado': reserva[6]
            }
        return None

    def close(self):
        self.db_service.close()
