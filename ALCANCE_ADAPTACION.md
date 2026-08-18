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
| **Hito 4 — Reservas + Reclamos + Documentación** | Flujo completo de reservas, concurrencia, reclamos, seed de desarrollo, documentación | `bd8fe28`, `1cb56af` |

### Hito en Curso / Pendiente

| Hito | Estado | Próximo objetivo |
|---|---|---|
| **Hito 4.4 — Fundamentos transaccionales** | ⏳ Pendiente | Corregir patrón transaccional (conexiones compartidas entre modelos) |

> ⚠️ **Freeze transaccional vigente:** Hasta iniciar el Hito 4.4, no modificar `reserva_model.py`, `cancha_model.py`, `buscar_complejos_view.py` ni el flujo de reservas.
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
| **DatabaseService multi-conexión** | 🟡 Deuda arquitectónica | Cada modelo crea su propia conexión; sin atomicidad real entre `DELETE disponibilidad` e `INSERT reserva`. Se corrige en Hito 4.4. |
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
| 7 | Reservar cancha | Alta | ✅ Implementado (deuda arquitectónica: conexiones independientes, ver Hito 4.4) |
| 8 | Ver/Cancelar mis reservas | Alta | ✅ Implementado |
| 9 | Editar mi perfil | Media | ✅ Heredado funcional |
| 10 | Panel admin con resumen de reservas | Media | ⏳ Pendiente |
| 11 | Sistema de reclamos | Baja | ✅ Implementado (Hito 4.2) |
---

## 5. Bugs Conocidos

Ver [BUGS.md](./BUGS.md) para el registro detallado.

**Resumen:**
- BUG-003: Login no retorna `rut` (corregido en Hito 4.2)
- BUG-005/006: Vistas con SQL directo omiten campos opcionales (baja prioridad)
- **BUG 4.1.4:** Error "No se pudo realizar la reserva" — archivado, su causa raíz es la deuda arquitectónica del patrón transaccional (conexiones independientes). Se corrige en Hito 4.4.
- **Deuda arquitectónica:** `DatabaseService` crea conexiones independientes por instancia. Ver [HITO_4_SEGUIMIENTO.md](./HITO_4_SEGUIMIENTO.md) para detalle.
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
