# ArriendoCanchas.cl

Plataforma de arriendo de canchas deportivas construida con **Flet + PostgreSQL**.

> ⚠️ **Nota:** Este repositorio es una adaptación personal del proyecto original
> [arriendocanchas](https://github.com/HernanEspinozaDev/arriendocanchas).
> Se redujo de 6 roles a 2 (Administrador y Usuario), se migró el hashing
> de contraseñas de `crypt()` de PostgreSQL a `passlib`, y se cargan las
> credenciales desde variables de entorno.

---

## Estado del Proyecto

| Hito | Estado | Descripción |
|---|---|---|
| **Hito 0** | ✅ Completado | Preparación del entorno (variables de entorno, passlib, BD local) |
| **Hito 1** | ✅ Completado | Schema SQL, seed data, documentación de bugs |
| **Hito 2** | ✅ Completado | Consolidación de roles (6 → 2: Administrador, Usuario) |
| **Hito 3** | ✅ Completado | Protección de rutas autenticadas con `route_guard` |
| **Hito 4.1** | 🟡 ~85% | **Reservas** — En validación funcional |
| **Hito 4.2** | ⏳ Pendiente | Reclamos |
| **Hito 4.3** | ⏳ Pendiente | Gestión administrativa (CRUD Complejos/Canchas/Disponibilidades) |

---

## Requisitos

- Python 3.10–3.12 (no 3.13, Flet puede tener incompatibilidades)
- PostgreSQL 15+
- pip

## Instalación
