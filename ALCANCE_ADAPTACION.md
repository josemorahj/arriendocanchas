# ALCANCE_ADAPTACION.md

## Proyecto: ArriendoCanchas — Versión Personal

---

## 1. Objetivo del proyecto

Crear una **versión propia y deployable** de una plataforma de arriendo de canchas deportivas,
tomando como base el repositorio heredado `arriendocanchas`.

**Meta final:** Una app web funcional donde:
- Un administrador gestiona sus complejos, canchas y disponibilidad.
- Usuarios (clientes) se registran, buscan canchas disponibles y reservan.
- Todo desplegado en Render o Railway con PostgreSQL.

---

## 2. Estado Actual (Julio 2026)

### Hitos Completados

| Hito | Descripción | Commit |
|---|---|---|
| **Hito 0 — Entorno** | Variables de entorno, migración a passlib, BD local | `78366d4`, `8cf3d1a` |
| **Hito 1 — Schema + Bugs** | schema.sql desde código fuente, documentación de bugs | `23fe659` |
| **Hito 2 — Roles** | Consolidación de 6 roles → 2 (Administrador, Usuario) | `2f94cc1` |
| **Hito 3 — Rutas** | route_guard, protección de rutas autenticadas | `2f94cc1` |

### Hito en Curso

| Hito | Estado | Próximo objetivo |
|---|---|---|
| **Hito 4.1 — Reservas** | 🟡 ~85%, en validación funcional | Identificar excepción en reserva |
| **Hito 4.2 — Reclamos** | ⏳ Pendiente | Revisar sesión (rut), MisReclamosView, estado, id_admin_responsable |
| **Hito 4.3 — Gestión Admin** | ⏳ Pendiente | CRUD Complejos, CRUD Canchas, CRUD Disponibilidades |
---

## 3. Decisiones de Arquitectura ya Implementadas

| Decisión | Estado | Detalle |
|---|---|---|
| **Reducir de 6 a 2 roles** | ✅ Implementado | Solo Administrador y Usuario |
| **passlib en lugar de crypt()** | ✅ Implementado | `security/passwords.py` con `CryptContext` |
| **Variables de entorno** | ✅ Implementado | `database_service.py` usa `os.getenv()` + `dotenv` |
| **route_guard** | ✅ Implementado | Middleware de protección de rutas en `route_guard.py` |
| **Flet como UI** | ✅ Mantenido | Sin migración a otra tecnología |
| **PostgreSQL como BD** | ✅ Mantenido | Sin migración a SQLite |
---

## 4. Funcionalidades del MVP

| # | Funcionalidad | Prioridad | Estado |
|---|---|---|---|
| 1 | Landing page pública | Alta | ✅ Heredado funcional |
| 2 | Registro de usuarios | Alta | ✅ Implementado |
| 3 | Inicio de sesión | Alta | ✅ Adaptado a passlib |
| 4 | CRUD Complejos (admin) | Alta | ⏳ Por validar en Hito 4.3 |
| 5 | CRUD Canchas + Disponibilidad (admin) | Alta | ✅ Implementado, bugs corregidos |
| 6 | Buscar complejos y canchas disponibles | Alta | ✅ Implementado |
| 7 | Reservar cancha | Alta | 🟡 En validación (bug 4.1.4 bloqueante) |
| 8 | Ver/Cancelar mis reservas | Alta | ✅ Implementado |
| 9 | Editar mi perfil | Media | ✅ Heredado funcional |
| 10 | Panel admin con resumen de reservas | Media | ⏳ Pendiente |
| 11 | Sistema de reclamos | Baja | ⏳ Pendiente (Hito 4.2) |
---

## 5. Bugs Conocidos

Ver [BUGS.md](./BUGS.md) para el registro detallado.

**Resumen:**
- BUG-003: Login no retorna `rut` (se corrige en Hito 4.2)
- BUG-005/006: Vistas con SQL directo omiten campos opcionales (baja prioridad)
- **BUG 4.1.4 🔴:** Error "No se pudo realizar la reserva" (bloqueante para Hito 4.1)
---

## 6. Hosting Objetivo

| Opción | Prioridad | Estado |
|---|---|---|
| Render (Web Service + PostgreSQL) | 1ª | Pendiente — se abordará post-Hito 4 |
| Railway | 2ª | Alternativa si cambian condiciones de Render |
| Local + ngrok | 3ª | Para demos rápidas |
---

## 7. Lo que NO incluye el MVP

- Pagos en línea
- Notificaciones por email
- Subida de imágenes
- Calendario visual
- App móvil
- Multi-idioma
- Multi-complejo avanzado

