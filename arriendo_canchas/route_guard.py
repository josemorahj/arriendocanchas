ROUTE_ROLES = {
    "/dashboard": ["Administrador", "Usuario"],
    "/mis_complejos": ["Administrador"],
    "/mis_canchas": ["Administrador"],
    "/gestion_reclamos": ["Administrador"],
    "/mis_datos": ["Usuario"],
    "/buscar_complejos": ["Usuario"],
    "/mis_reservas": ["Usuario"],
    "/mis_reclamos": ["Usuario"],
}


def require_role(user_vm, route: str) -> str:
    """
    Verifica si el usuario autenticado tiene permiso para acceder a la ruta.

    Retorna:
        "OK"          -> El usuario está autenticado y autorizado,
                         o la ruta no está protegida.
        "NO_SESSION"  -> No hay sesión activa (user_vm.get_user() es None/falsy).
        "FORBIDDEN"   -> El usuario está autenticado pero su tipo_cuenta
                         no está en la lista de roles permitidos para la ruta.
    """
    user = user_vm.get_user()

    # Si no hay sesión activa
    if not user:
        return "NO_SESSION"

    # Si la ruta no está en el diccionario, no está protegida
    if route not in ROUTE_ROLES:
        return "OK"

    # Obtener el tipo de cuenta del usuario autenticado
    user_type = user.get("tipo_cuenta")

    # Verificar si el tipo de cuenta está autorizado para esta ruta
    if user_type in ROUTE_ROLES[route]:
        return "OK"
    else:
        return "FORBIDDEN"
