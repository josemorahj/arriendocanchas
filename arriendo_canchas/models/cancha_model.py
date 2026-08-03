import psycopg2
from services.database_service import DatabaseService

class CanchaModel:
    def __init__(self):
        self.db_service = DatabaseService()
        self.cursor = self.db_service.cursor

    def fetch_canchas(self, id_usuario):
        query = """
        SELECT c.id_cancha, c.nombre_cancha, c.tipo_cancha, co.nombre_complejo, c.id_imagen
        FROM Canchas c
        JOIN ComplejosDeportivos co ON c.id_complejo = co.id_complejo
        WHERE co.id_usuario = %s
        """
        self.cursor.execute(query, (id_usuario,))
        canchas = self.cursor.fetchall()
        return [{
            'id_cancha': c[0],
            'nombre_cancha': c[1],
            'tipo_cancha': c[2],
            'complejo_nombre': c[3],
            'id_imagen': c[4]
        } for c in canchas]

    def add_cancha(self, nombre_cancha, tipo_cancha, id_complejo, fecha_disponibilidad, id_imagen=None):
        query = """
        INSERT INTO Canchas (nombre_cancha, tipo_cancha, id_complejo, fecha_disponibilidad, id_imagen)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (nombre_cancha, tipo_cancha, id_complejo, fecha_disponibilidad, id_imagen))
        self.db_service.connection.commit()

    def update_cancha(self, id_cancha, nombre_cancha, tipo_cancha, id_complejo, fecha_disponibilidad, id_imagen=None):
        query = """
        UPDATE Canchas
        SET nombre_cancha = %s, tipo_cancha = %s, id_complejo = %s, fecha_disponibilidad = %s, id_imagen = %s
        WHERE id_cancha = %s
        """
        self.cursor.execute(query, (nombre_cancha, tipo_cancha, id_complejo, fecha_disponibilidad, id_imagen, id_cancha))
        self.db_service.connection.commit()

    def delete_cancha(self, id_cancha):
        query = "DELETE FROM Canchas WHERE id_cancha = %s"
        self.cursor.execute(query, (id_cancha,))
        self.db_service.connection.commit()

    def fetch_cancha_by_id(self, id_cancha):
        query = """
        SELECT c.id_cancha, c.nombre_cancha, c.tipo_cancha, co.nombre_complejo, c.id_imagen
        FROM Canchas c
        JOIN ComplejosDeportivos co ON c.id_complejo = co.id_complejo
        WHERE c.id_cancha = %s
        """
        self.cursor.execute(query, (id_cancha,))
        cancha = self.cursor.fetchone()
        if cancha:
            return {
                'id_cancha': cancha[0],
                'nombre_cancha': cancha[1],
                'tipo_cancha': cancha[2],
                'complejo_nombre': cancha[3],
                'id_imagen': cancha[4]
            }
        return None

    def fetch_canchas_by_complejo(self, id_complejo):
        query = """
        SELECT id_cancha, nombre_cancha, tipo_cancha
        FROM Canchas
        WHERE id_complejo = %s
        """
        self.cursor.execute(query, (id_complejo,))
        canchas = self.cursor.fetchall()
        return [{
            'id_cancha': c[0],
            'nombre_cancha': c[1],
            'tipo_cancha': c[2]
        } for c in canchas]

    def fetch_disponibilidad(self, id_cancha):
        query = """
        SELECT id_disponibilidad, fecha, hora_inicio, hora_fin
        FROM DisponibilidadCanchas
        WHERE id_cancha = %s
        ORDER BY fecha, hora_inicio
        """
        self.cursor.execute(query, (id_cancha,))
        disponibilidad = self.cursor.fetchall()
        return [{
            'id_disponibilidad': d[0],
            'fecha': d[1],
            'hora_inicio': d[2],
            'hora_fin': d[3]
        } for d in disponibilidad]

    def add_disponibilidad(self, id_cancha, fecha, hora_inicio, hora_fin):
        query = """
        INSERT INTO DisponibilidadCanchas (id_cancha, fecha, hora_inicio, hora_fin)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (id_cancha, fecha, hora_inicio, hora_fin))
            self.db_service.connection.commit()
        except Exception:
            self.db_service.connection.rollback()
            raise

    def update_disponibilidad(self, id_disponibilidad, fecha, hora_inicio, hora_fin):
        query = """
        UPDATE DisponibilidadCanchas
        SET fecha = %s, hora_inicio = %s, hora_fin = %s
        WHERE id_disponibilidad = %s
        """
        try:
            self.cursor.execute(query, (fecha, hora_inicio, hora_fin, id_disponibilidad))
            self.db_service.connection.commit()
        except Exception:
            self.db_service.connection.rollback()
            raise

    def delete_disponibilidad(self, id_disponibilidad, connection=None):
        query = "DELETE FROM DisponibilidadCanchas WHERE id_disponibilidad = %s"
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute(query, (id_disponibilidad,))
            return cursor.rowcount
        self.cursor.execute(query, (id_disponibilidad,))
        return self.cursor.rowcount

    def close(self):
        self.db_service.close()
