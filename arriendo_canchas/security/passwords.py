# security/passwords.py
#
# Módulo central de seguridad para contraseñas.
# Único punto de configuración del algoritmo de hashing.
# Todos los archivos deben importar pwd_context desde aquí.

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)
