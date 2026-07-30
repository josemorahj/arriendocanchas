# Hito 4 — Seguimiento de Estado

> **Última actualización:** Julio 2026
> **Estado general:** ✅ Hito 4 completado
> **Freeze transaccional vigente hasta iniciar Hito 4.4**

---

## Resumen de entregables

| Tarea | Estado | Commit | Descripción |
|---|---|---|---|
| **Hito 4.1 — Robustez de reservas** | ✅ Completado | `bd8fe28` | Flujo completo de reservas, control transaccional, concurrencia, Mis Reservas con hora_inicio/hora_fin |
| **Hito 4.2 — Gestión de reclamos** | ✅ Completado | `bd8fe28` | Sistema de reclamos implementado |
| **Tarea 4.3.1 — Seed de desarrollo** | ✅ Completado | `1cb56af` | `seed_disponibilidad_dev.sql` — semilla idempotente para 3 disponibilidades en id_cancha=1 |
| **Tarea 4.3.2 — Verificación add_reserva()** | ✅ Cerrada por verificación | — | No existe duplicación activa de `add_reserva()`. Eliminada del backlog. |
| **Tarea 4.3.3 — Actualización de documentación** | ✅ Completado | — | README, HITO_4_SEGUIMIENTO, BUGS, ALCANCE_ADAPTACION actualizados |

---

## Hito 4.1 — Robustez del flujo de reservas
Estado: ✅ Completado (100%)

### Objetivo

Garantizar un flujo de reservas consistente, incorporando horas de inicio y término, control transaccional y protección frente a reservas concurrentes.

### Funcionalidades implementadas (detalle archivado)

**Modelo de reservas**
- `hora_inicio` incorporada en las consultas.
- `hora_fin` incorporada en las consultas.
- Eliminada la duplicidad de `add_reserva()` (BUG-004).
- Inserción de reservas con fecha, hora de inicio y hora de fin.

**Disponibilidad**
- `fetch_canchas_by_complejo()` creado para eliminar SQL inline en la vista.
- `delete_disponibilidad()` ahora retorna `rowcount`.
- Eliminado el `commit()` interno de `delete_disponibilidad()` para permitir control transaccional.

**Protección contra concurrencia**
- Estrategia: `DELETE` + verificar `rowcount` + `INSERT`.
- Si `rowcount == 0` (otro usuario reservó antes): rollback y mensaje al usuario.
- Si `rowcount > 0`: proseguir con INSERT y commit.

### Resumen de estado (archivado)

| Área | Estado |
|---|---|
| Modelo de reservas | ✅ |
| Disponibilidad | ✅ |
| Validaciones | ✅ |
| Control transaccional | 🟡 Ver deuda arquitectónica |
| Flujo completo de reserva | ✅ |
| Mis Reservas | ✅ |
| Concurrencia | 🟡 Ver deuda arquitectónica |

---

## Hito 4.2 — Gestión de reclamos
Estado: ✅ Completado

### Funcionalidades implementadas
- Modelo `ReclamoModel` con `add_reclamo()`, `fetch_reclamos()`.
- Vista `mis_reclamos_view.py` para usuarios.
- Vista `gestion_reclamos_view.py` para administradores.
- Integración con el flujo de reservas.

---

## Tarea 4.3.1 — Seed de desarrollo
Estado: ✅ Completado (commit `1cb56af`)

### Detalle
- Archivo: `arriendo_canchas/seed_disponibilidad_dev.sql`
- Propósito: Poblar disponibilidades para `id_cancha = 1` en desarrollo.
- Idempotente: usa `WHERE NOT EXISTS`.
- No modifica usuarios, complejos, canchas, reservas ni reclamos.

---

## Tarea 4.3.2 — Verificación de add_reserva()
Estado: ✅ Cerrada por verificación

### Hallazgo
No existe duplicación activa de `add_reserva()` en el código actual. La duplicación pertenecía al historial de desarrollo y fue eliminada durante el Hito 4.1. Se elimina del backlog.

---

## Deuda arquitectónica — Patrón transaccional (pendiente para Hito 4.4)

### Problema detectado
`DatabaseService` crea una conexión PostgreSQL **por instancia**. Esto significa que:

```
CanchaModel
  ↓
  DatabaseService() → Conexión A

ReservaModel
  ↓
  DatabaseService() → Conexión B
```

**Consecuencia:** El flujo de reservas ejecuta:
1. `DELETE disponibilidad` → Conexión A
2. `INSERT reserva` → Conexión B

Ambas operaciones ocurren en conexiones distintas, por lo que **no existe atomicidad real** entre ellas. Una transacción iniciada en la Conexión A no incluye a la Conexión B.

### Solución propuesta (Hito 4.4)
Implementar un mecanismo de conexión compartida que garantice atomicidad entre ambas operaciones (ej: DatabaseService singleton, pool de conexiones, o inyección de同一 conexión entre modelos).

### Freeze transaccional
Hasta iniciar oficialmente el Hito 4.4, **no modificar**:
- `arriendo_canchas/models/reserva_model.py`
- `arriendo_canchas/models/cancha_model.py`
- `arriendo_canchas/views/authenticated/buscar_complejos_view.py`
- Ni ningún archivo que coordine la transacción de reservas.

Se permiten cambios en: documentación, scripts SQL, seeds y otras funcionalidades no relacionadas con reservas.

### BUG 4.1.4 (archivado)
- **Estado:** Cerrado — la excepción era consecuencia de la deuda arquitectónica (conexiones independientes).
- **Corrección:** Se abordará dentro del Hito 4.4 al resolver el patrón transaccional.

---

## Próximo hito: Hito 4.4 — Fundamentos transaccionales

### Objetivo
Resolver la deuda arquitectónica de conexiones independientes entre modelos para garantizar atomicidad real en el flujo de reservas.

### Plan tentativo
1. Diseñar el mecanismo de conexión compartida.
2. Implementar la solución.
3. Corregir el BUG 4.1.4 como consecuencia.
4. Validar: reserva exitosa + prueba de concurrencia.
5. Cierre del Hito 4 completo.
