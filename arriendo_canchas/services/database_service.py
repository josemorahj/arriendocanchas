# services/database_service.py

import os
from contextlib import contextmanager
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()


class DatabaseService:
    def __init__(self):
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "5432"))
        dbname = os.getenv("DB_NAME", "arriendocanchas")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD")
        schema = os.getenv("DB_SCHEMA", "public")

        if not password:
            raise ValueError(
                "DB_PASSWORD no está configurada. "
                "Verifica que exista un archivo .env en la raíz del proyecto "
                "o que la variable de entorno esté definida en el sistema."
            )

        self.connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
        self.cursor = self.connection.cursor()

        # Configurar search_path usando Identifier para evitar SQL injection
        try:
            self.cursor.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(schema))
            )
            self.connection.commit()
        except Exception as e:
            print(f"Error al establecer search_path: {e}")
            self.close()
            raise e

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    @contextmanager
    def transaction(self):
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
