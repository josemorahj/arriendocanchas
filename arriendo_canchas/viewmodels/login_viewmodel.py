# viewmodels/login_viewmodel.py

from services.database_service import DatabaseService
from security.passwords import pwd_context

class LoginViewModel:
    def __init__(self):
        pass

    def login(self, correo, contrasena):
        db_service = DatabaseService()
        try:
            query = """
            SELECT id_usuario, nombre, tipo_cuenta, contrasena
            FROM usuarios
            WHERE correo = %s
            """
            db_service.cursor.execute(query, (correo,))
            user = db_service.cursor.fetchone()
            if user:
                user_id, nombre, tipo_cuenta, hashed_password = user
                # Verificar la contraseña con passlib
                try:
                    password_match = pwd_context.verify(contrasena, hashed_password)
                except Exception:
                    # Hash corrupto o no identificable -> autenticación fallida
                    password_match = False
                if password_match:
                    # Devolver los datos del usuario
                    user_data = {
                        'id_usuario': user_id,
                        'nombre': nombre,
                        'tipo_cuenta': tipo_cuenta,
                        'correo': correo,
                    }
                    return user_data
            return None
        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            return None
        finally:
            db_service.close()

