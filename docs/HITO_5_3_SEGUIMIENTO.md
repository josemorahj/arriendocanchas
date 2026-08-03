# Hito 5.3 — Seguimiento de Estado

> **Última actualización:** Cierre del Hito 5.3
> **Estado general:** ✅ Hito 5.3 completado y cerrado
> **Próximo trabajo:** Hito 5.3-bis (backlog) — pendiente de instrucción formal

---

## Resumen de entregables

| Tarea | Estado | Descripción |
|---|---|---|
| **5.3.1 — Soporte `connection=None` en `cancha_model.py`** | ✅ Completado | Métodos de disponibilidad aceptan `connection` opcional |
| **5.3.2 — Soporte `connection=None` en `reserva_model.py`** | ✅ Completado | `add_reserva()` acepta `connection` opcional |
| **5.3.3 — Soporte de modelos involucrados en el flujo** | ✅ Completado | Compatibilidad de firma sin romper call-sites |
| **5.3.4-A — `DatabaseService.transaction()`** | ✅ Completado | Context manager que centraliza `commit()` / `rollback()` |
| **5.3.4-B — Integración transaccional en `buscar_complejos_view.py`** | ✅ Completado | Flujo de reserva usa `transaction()` + `connection=` |
| **5.3.5 — Validación integrada de la transacción de reserva** | ✅ Completado | Tres escenarios verificados sobre PostgreSQL local |

---

## Hito 5.3 — Cierre formal
Estado: ✅ Completado (100%)

### Objetivo
Centralizar el control transaccional del flujo de reservas en `DatabaseService.transaction()`,
garantizando atomicidad (eliminar disponibilidad + crear reserva en un único commit/rollback).

### Implementación de `DatabaseService.transaction()`
- Context manager que recibe la conexión activa del `DatabaseService`.
- Al cerrar el contexto con éxito → `commit()`.
- Si alguna operación interna lanza excepción → `rollback()` y re-lanza la excepción.
- Único responsable de `commit()` / `rollback()` dentro del flujo de reservas.

### Integración del flujo transaccional de reservas
- `buscar_complejos_view.py` ahora usa `with cancha_model.db_service.transaction() as connection`.
- `delete_disponibilidad(..., connection=connection)` y `add_reserva(..., connection=connection)`
  se ejecutan sobre la misma conexión dentro de la transacción.
- Si `delete_disponibilidad` afecta 0 filas → no se crea la reserva (mensaje "Horario No Disponible").
- Si `add_reserva` falla → `transaction()` ejecuta `rollback()` y se restaura la disponibilidad.

### Validación de los tres escenarios (Tarea 5.3.5)
Sobre PostgreSQL **local** (`arriendocanchas_local`, host `localhost`), verificados:

1. **Reserva exitosa** — la disponibilidad se elimina y se crea exactamente una reserva
   con datos coincidentes, sin duplicación. La aplicación muestra "Reserva Exitosa".
2. **Disponibilidad inexistente** — `delete_disponibilidad()` afecta 0 filas, no se crea una
   segunda reserva y la cantidad de reservas no cambia. La aplicación muestra "Horario No Disponible".
3. **Rollback al fallar `add_reserva()`** — al provocar una violación de llave foránea real
   (restricción de base de datos), `transaction()` ejecuta `rollback()`: la reserva no se crea,
   la disponibilidad se restaura y la conexión sigue operativa.

No se detectaron fallos de atomicidad durante las pruebas.

### Cierre exitoso del Hito 5.3
Con las tareas 5.3.1 a 5.3.5 implementadas y verificadas, el Hito 5.3 queda **técnicamente terminado
y cerrado formalmente**.

---

## Nota sobre `commit()` / `rollback()` (alcance preciso)

Dentro del flujo de reservas (`buscar_complejos_view.py`) **ya no existen** `commit()`, `rollback()`
ni `autocommit`. El control transaccional de ese flujo quedó **centralizado en `DatabaseService.transaction()`**.

Las demás apariciones de `commit()` y `rollback()` en el repositorio pertenecen a **módulos fuera del
alcance del Hito 5.3** (p. ej. `canchas_view.py`, `complejos_view.py`, `mis_reservas_view.py`,
`mis_reclamos_view.py` y los modelos no involucrados en el flujo de reserva), y permanecen planificadas
para el **backlog Hito 5.3-bis**.

> ⚠️ Estas llamadas **NO desaparecieron de todo el repositorio**. Solo el flujo de reservas
> (`buscar_complejos_view.py`) centralizó su control transaccional en `DatabaseService.transaction()`.

---

## Próximo hito: Hito 5.3-bis (backlog, pendiente)

Sin iniciar aún. Queda planificada la migración de los módulos que aún conservan control transaccional
manual: `canchas_view.py`, `complejos_view.py`, `mis_reservas_view.py`, `mis_reclamos_view.py`,
`mis_datos_view.py`, `gestion_reclamos_view.py`, `login_viewmodel.py` y los modelos no involucrados
en el flujo de reserva (`complejo_model.py`, `reclamo_model.py`, `usuario_model.py`).
