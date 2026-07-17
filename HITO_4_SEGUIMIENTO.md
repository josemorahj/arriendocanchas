# Hito 4 — Seguimiento de Estado

> **Última actualización:** 16-07-2026

---

## Hito 4.1 — Robustez del flujo de reservas
Estado: 🟡 En validación funcional (85%)

### Objetivo

Garantizar un flujo de reservas consistente, incorporando horas de inicio y término, control transaccional y protección frente a reservas concurrentes.

### Funcionalidades implementadas
**Modelo de reservas**
- `hora_inicio` incorporada en las consultas.
- `hora_fin` incorporada en las consultas.
- Eliminada la duplicidad de `add_reserva()` (BUG-004).
- Inserción de reservas con fecha, hora de inicio y hora de fin.

**Disponibilidad**
- `fetch_canchas_by_complejo()` creado para eliminar SQL inline en la vista.
- `delete_disponibilidad()` ahora retorna `rowcount`.
- Eliminado el `commit()` interno de `delete_disponibilidad()` para permitir control transaccional.

**Flujo de reserva implementado**
1. Buscar complejo
2. Seleccionar cancha
3. Abrir disponibilidad
4. Seleccionar horario
5. Eliminar disponibilidad
6. Guardar reserva
7. Commit / Rollback

**Protección contra concurrencia**

### Bloqueantes actuales

**BUG 4.1.4**
- **Estado:** 🔴 Abierto
- **Descripción:** Al confirmar una reserva, el flujo entra al bloque `except` de `reservar_cancha()`, ejecutando `rollback` y mostrando el mensaje: `No se pudo realizar la reserva.`
- **Pendiente:** Identificar la excepción real mediante traceback antes de diseñar o implementar cualquier corrección.

### Resumen de estado

| Área | Estado |
|---|---|
| Modelo de reservas | ✅ |
| Disponibilidad | ✅ |
| Validaciones | ✅ |
| Control transaccional | 🟡 |
| Flujo completo de reserva | 🟡 |
| Mis Reservas | ⏳ |
| Concurrencia | ⏳ |

**Avance estimado del Hito 4.1:** 85%

### Próxima sesión

**Objetivo**

Resolver el BUG 4.1.4.

**Plan de trabajo**

1. Instrumentar el bloque `except` de `reservar_cancha()`.
2. Obtener el traceback completo.
3. Identificar la línea exacta de la excepción.
4. Diseñar la solución.
5. Implementar la corrección.
6. Validar una reserva exitosa.
7. Validar la vista Mis Reservas.
8. Ejecutar la prueba de concurrencia.
9. Cerrar el Hito 4.1.

