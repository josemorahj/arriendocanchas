# BUGS.md — Registro de Bugs e Inconsistencias

> **Contexto:** Este archivo documenta bugs encontrados durante el desarrollo,
> tanto los ya corregidos como los pendientes.
>
> **Última actualización:** Hito 4.1 — Reservas
---

## Bugs Corregidos
### BUG-001: fetch_reservas() no incluye hora_inicio/hora_fin ✅

- **Archivo:** `models/reserva_model.py` — método `fetch_reservas()`
- **Problema:** El SELECT solo devolvía 5 columnas sin `hora_inicio` ni `hora_fin`.
- **Impacto:** `MisReservasView` lanzaba `KeyError` al intentar mostrar horas.
- **Solución:** Se agregaron `hora_inicio` y `hora_fin` a la consulta.
- **Corregido en:** Hito 4.1

### BUG-002: fetch_reserva_by_id() mismo problema ✅

- **Archivo:** `models/reserva_model.py` — método `fetch_reserva_by_id()`
- **Problema:** Mismo SELECT incompleto sin `hora_inicio`/`hora_fin`.
- **Solución:** Se agregaron ambos campos a la consulta.
- **Corregido en:** Hito 4.1

### BUG-003: Login no retorna 'rut' (Pendiente para Hito 4.2)

- **Archivo:** `viewmodels/login_viewmodel.py` y `views/authenticated/mis_reclamos_view.py`
- **Problema:** `login()` no incluye `rut` en el diccionario `user_data`.
- **Impacto:** `MisReclamosView` lanza `KeyError` al acceder a `user_vm.get_user()['rut']`.
- **Estado:** Pendiente — se corregirá en Hito 4.2 (Reclamos)

### BUG-004: Dos definiciones de add_reserva() ✅

- **Archivo:** `models/reserva_model.py`
- **Problema:** Existían dos definiciones de `add_reserva()`; la segunda sobreescribía a la primera.
- **Solución:** Se eliminó la definición redundante (versión sin hora_inicio/hora_fin).
- **Corregido en:** Hito 4.1

### BUG-005: canchas_view.sql directo omite fecha_disponibilidad e id_imagen
(Pendiente — baja prioridad, campos opcionales)

### BUG-006: complejos_view.sql directo omite telefono, correo, id_imagen, cantidad_canchas
(Pendiente — baja prioridad, campos opcionales)
---

## Bugs del Hito 4.1 — Reservas

### BUG 4.1.1: fullscreen=True en AlertDialog ✅

- **Estado:** Corregido
- **Síntoma:** El botón del reloj (ACCESS_TIME) en Gestionar Canchas no abría el diálogo de disponibilidad.
- **Causa:** `AlertDialog(fullscreen=True)` — parámetro no soportado por la versión actual de Flet.
- **Solución:** Eliminar `fullscreen=True` del AlertDialog en `open_disponibilidad_dialog()`.
- **Archivo:** `views/authenticated/canchas_view.py` — línea 535
- **Corregido el:** 16-07-2026

### BUG 4.1.2: Errores de formato e indentación ✅

- **Estado:** Corregido
- **Problema:** Problemas de formato e indentación durante la implementación.
- **Validaciones:** `py_compile` exitoso, `git diff --check` limpio.

### BUG 4.1.3: Cuentas de prueba sin contraseña funcional ✅

- **Estado:** Resuelto
- **Problema:** Las cuentas admin@test.cl y user@test.cl no tenían contraseñas válidas con el nuevo sistema de hashing (passlib).
- **Solución:** Script temporal que regeneró los hashes con `pwd_context.hash("Prueba123!")`.
- **Corregido el:** 16-07-2026

### BUG 4.1.4: Error "No se pudo realizar la reserva" 🔴 BLOQUEANTE

- **Estado:** Pendiente de diagnóstico
- **Síntoma:** El flujo de reserva entra al bloque `except` de `reservar_cancha()` y muestra el mensaje "No se pudo realizar la reserva."
- **Información conocida:**
  - Se ejecuta rollback automático.
  - La excepción exacta aún no ha sido identificada (falta instrumentar el bloque `except`).
- **Próxima acción:** Instrumentar el bloque `except` para capturar el traceback completo e identificar la línea exacta que lanza la excepción.
- **Archivo:** `views/authenticated/buscar_complejos_view.py`

