# BUGS.md — Registro de Inconsistencias Detectadas

> **Contexto:** Hallazgos realizados durante la reconstrucción de schema.sql (HITO 1 — Fase 4),
> al cruzar el código fuente real (models/, views/, viewmodels/) contra las consultas SQL
> y los datos esperados por las vistas.
>
> **Propósito:** Documentar para su corrección en un hito posterior (HITO 3 — auditoría funcional).
> No corregir hasta entonces.

---

## 1. fetch_reservas() no incluye hora_inicio/hora_fin

- **Componente/archivo afectado:** `arriendo_canchas/models/reserva_model.py` — método `fetch_reservas()`
- **Descripción breve de la inconsistencia:** El método `fetch_reservas()` ejecuta un SELECT que solo devuelve 5 columnas (`id_reserva`, `nombre`, `nombre_cancha`, `fecha_reserva`, `estado`), sin incluir `hora_inicio` ni `hora_fin`. Sin embargo, `MisReservasView` renderiza columnas de hora y accede a `r['hora_inicio']` y `r['hora_fin']`, que no existen en el diccionario devuelto.
- **Riesgo/impacto:** La vista `MisReservasView` lanzará un `KeyError` en tiempo de ejecución al intentar mostrar las horas de cada reserva, dejando la página en blanco o con error.
- **Estado:** Pendiente — hito posterior (HITO 3, auditoría funcional)

---

## 2. fetch_reserva_by_id() mismo problema que punto 1

- **Componente/archivo afectado:** `arriendo_canchas/models/reserva_model.py` — método `fetch_reserva_by_id()`
- **Descripción breve de la inconsistencia:** El método `fetch_reserva_by_id()` ejecuta el mismo SELECT de 5 columnas sin `hora_inicio` ni `hora_fin`. Cualquier código que consuma este método espere esos campos, recibirá un diccionario incompleto.
- **Riesgo/impacto:** Si alguna vista o servicio utiliza `fetch_reserva_by_id()` y referencia `hora_inicio`/`hora_fin`, obtendrá un `KeyError`. Actualmente no hay consumidores directos detectados en el flujo principal, pero es una bomba de tiempo.
- **Estado:** Pendiente — hito posterior (HITO 3, auditoría funcional)

---

## 3. Login no retorna 'rut', pero mis_reclamos_view.py lo necesita

- **Componente/archivo afectado:** `arriendo_canchas/viewmodels/login_viewmodel.py` (método `login()`) y `arriendo_canchas/views/authenticated/mis_reclamos_view.py`
- **Descripción breve de la inconsistencia:** El método `login()` en `LoginViewModel` ejecuta `SELECT id_usuario, nombre, tipo_cuenta, contrasena FROM usuarios WHERE correo = %s` y construye el diccionario `user_data` con las llaves `id_usuario`, `nombre`, `tipo_cuenta`, `correo`. No incluye `rut`. Sin embargo, `MisReclamosView` llama a `user_vm.get_user()['rut']` al inicializarse.
- **Riesgo/impacto:** Al abrir la vista de reclamos, se lanza un `KeyError` porque la llave `'rut'` no existe en el diccionario del usuario autenticado. La funcionalidad de reclamos queda inaccesible.
- **Estado:** Pendiente — hito posterior (HITO 3, auditoría funcional)

---

## 4. Dos definiciones de add_reserva() — la segunda sobreescribe a la primera

- **Componente/archivo afectado:** `arriendo_canchas/models/reserva_model.py`
- **Descripción breve de la inconsistencia:** Existen dos definiciones del método `add_reserva()` en la misma clase. La primera (líneas ~30-38) tiene firma `add_reserva(self, id_usuario, id_cancha, fecha_reserva, estado='Confirmada')` e inserta sin `hora_inicio`/`hora_fin`. La segunda (líneas ~43-50) tiene firma `add_reserva(self, id_usuario, id_cancha, fecha_reserva, hora_inicio, hora_fin, estado='Confirmada')` e inserta incluyendo `hora_inicio`/`hora_fin`. En Python, la segunda definición sobreescribe completamente a la primera, por lo que la versión activa es la que incluye horas.
- **Riesgo/impacto:** El código es confuso y propenso a errores de mantenimiento. Cualquier llamada que use la firma antigua (sin horas) fallará con `TypeError`. La versión activa es correcta, pero la definición muerta es ruido que puede inducir a error.
- **Estado:** Pendiente — hito posterior (HITO 3, auditoría funcional)

---

## 5. canchas_view.py (SQL directo) no usa fecha_disponibilidad ni id_imagen

- **Componente/archivo afectado:** `arriendo_canchas/views/authenticated/canchas_view.py` (consultas SQL directas en `fetch_canchas()`, `save_new_cancha()`, `save_edit_cancha()`) vs `arriendo_canchas/models/cancha_model.py`
- **Descripción breve de la inconsistencia:** La vista `canchas_view.py` ejecuta consultas SQL directas que omiten `fecha_disponibilidad` e `id_imagen` en los INSERT y UPDATE de la tabla `Canchas`. En cambio, el modelo `cancha_model.py` sí incluye ambos campos. Como resultado, el CRUD desde la vista nunca persiste ni actualiza esos valores.
- **Riesgo/impacto:** Los valores de `fecha_disponibilidad` e `id_imagen` en la base de datos quedarán siempre como `NULL` cuando se gestionen canchas desde esta vista. Funcionalmente no hay error crítico porque ambos campos son opcionales, pero los datos almacenados serán incompletos.
- **Estado:** Pendiente — hito posterior (HITO 3, auditoría funcional)

---

## 6. complejos_view.py (SQL directo) omite telefono, correo, id_imagen, cantidad_canchas

- **Componente/archivo afectado:** `arriendo_canchas/views/authenticated/complejos_view.py` (consultas SQL directas en `fetch_complejos()`, `save_new_complejo()`, `save_edit_complejo()`) vs `arriendo_canchas/models/complejo_model.py`
- **Descripción breve de la inconsistencia:** La vista `complejos_view.py` ejecuta consultas SQL directas que omiten `telefono`, `correo`, `id_imagen` y `cantidad_canchas` en los INSERT y UPDATE de la tabla `ComplejosDeportivos`. El modelo `complejo_model.py` sí soporta todos estos campos.
- **Riesgo/impacto:** Los cuatro campos quedarán siempre como `NULL` cuando se gestionen complejos desde esta vista. Aunque son campos opcionales, se pierde la capacidad de almacenar información de contacto del complejo y el conteo de canchas, lo que afecta negativamente la experiencia del usuario y la completitud de los datos.
- **Estado:** Pendiente — hito posterior (HITO 3, auditoría funcional)
