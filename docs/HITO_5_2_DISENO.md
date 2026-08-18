# HITO 5.2 — Diseño de la Arquitectura de Acceso a PostgreSQL

> **Estado:** ✅ APROBADO (con dos ajustes respecto a la propuesta inicial).
> **Próximo hito:** Hito 5.3 (implementación) — ver alcance en la sección «Alcance de implementación (Hito 5.3)».
> **Verificación:** Artículo de verificación de fragmentos citados en la revisión crítica previa (evidencia literal en sección «Anexo — Verificación con evidencia»).

---

## 1. Contrato de `DatabaseService` (aprobado, sin cambios)

### 1.1 `DatabaseService.connection()`
- **Exclusivamente para operaciones simples** (lectura principalmente).
- Abre conexión, **ejecuta** el SQL, **NO ejecuta `commit()`**.
- **Cierra siempre** la conexión al finalizar (uso de `try/finally` o context manager).

### 1.2 `DatabaseService.transaction()`
- **Único contexto responsable de `commit()` / `rollback()`.**
- Se usa para **operaciones compuestas / atómicas** (ej. flujo de reserva).
- No hay transacciones anidadas ni savepoints.
- Al cerrar el contexto: si hubo éxito → `commit()`; si hubo excepción → `rollback()`.

### 1.3 Inyección por constructor (sin singleton global, sin framework de DI)
- `DatabaseService` se instancia **una sola vez en el arranque**.
- Se **entrega por constructor** a los modelos.
- **Sin singleton global.**
- **Sin framework de inyección de dependencias.**
- **Sin pools, sin Unit of Work, sin SQLAlchemy.**

### 1.4 Firma de métodos internos de un flujo compuesto
- Los métodos internos de un flujo compuesto **NO abren su propia conexión ni transacción**.
- **Reciben `connection` como parámetro** y solo ejecutan SQL.
- Un único método externo (ej. `reservar_cancha`) abre `with db_service.transaction()` y coordina
  a los métodos internos (verificar_disponibilidad, crear_reserva, eliminar_disponibilidad)
  **pasándoles la conexión activa**.

### 1.5 No se crea `reserva_service.py` en esta etapa
- El **propietario transaccional permanece en `reserva_model.py`** (o donde resida hoy la lógica de reserva).
- **No se introduce una capa de servicio adicional** hasta que exista una necesidad real de negocio compartida.

---

## 2. Alternativas evaluadas

| Alternativa | Evaluación | Decisión |
|---|---|---|
| **Singleton global** de `DatabaseService` | Resuelve la multi-conexión, pero introduce estado global implícito y dificulta pruebas unitarias | ❌ Descartado |
| **Framework de DI** (ej. injector, dependency-injector) | Aporta más estructura de la necesaria; agrega dependencia y complejidad | ❌ Descartado |
| **Conexión compartida vía inyección por constructor** | Una instancia única creada en el arranque, entregada a los modelos por constructor. Sin estado global, testeable, sin deps nuevas | ✅ **Aprobado** |
| **Pool de conexiones** | No se requiere volumen de concurrencia que lo justifique; añade complejidad | ❌ Descartado |
| **Unit of Work** | Sobredimensionado para el alcance actual; la atomicidad se resuelve con `transaction()` | ❌ Descartado |
| **SQLAlchemy** | Introduce ORM; cambio de paradigma mayor sin necesidad presente | ❌ Descartado |
| **Servicio de reserva separado (`reserva_service.py`)** | No existe aún necesidad de negocio compartida que lo justifique | ❌ Descartado (ver §1.5) |

---

## 3. Patrón de flujos

### 3.1 Flujo simple (lectura) — `connection()`
```
db_service.connection()
    ├─ método interno recibe connection (parámetro)
    │   └─ ejecuta SQL (SELECT)
    └─ cierra conexión siempre (sin commit)
```

### 3.2 Flujo compuesto / atómico — `transaction()`
```
with db_service.transaction() as conn:
    verificar_disponibilidad(conn, ...)     # solo SQL
    crear_reserva(conn, ...)                # solo SQL
    eliminar_disponibilidad(conn, ...)      # solo SQL
# commit() automático si todo sale bien
# rollback() automático si algo lanza excepción
```

---

## 4. Plan de migración de 6 pasos

> Cada paso debe validarse antes de continuar. El freeze permanece vigente
> sobre los 3 archivos de la Opción A hasta que se levante formalmente.

### Paso 1 — Ampliar `DatabaseService` con `connection()` y `transaction()`
- Mantener compatibilidad mínima inicial con `connection`/`cursor` mientras se migra (ver §5).
- Implementar `connection()` como context manager que abre y **siempre cierra**.
- Implementar `transaction()` como context manager que delega **único** commit/rollback al cerrar.
- Nota: hoy `DatabaseService.__init__` ejecuta `self.connection.commit()` al hacer `SET search_path`
  (`database_service.py:39`). Revisar si este commit debe moverse dentro del manejo de conexión.

### Paso 2 — Inyectar `DatabaseService` por constructor a `reserva_model.py`
- Definir `__init__(self, db_service)` y **eliminar** `self.db_service = DatabaseService()`.
- Cambiar la firma interna de `add_reserva` para **dejar de llamar `connection.commit()`** en su interior
  (motivo: en flujo compuesto el commit lo decide `transaction()`).
- Retirar la dependencia de `self.cursor` interno cuando corresponda.

### Paso 3 — Inyectar `DatabaseService` por constructor a `cancha_model.py`
- Mismo patrón que Paso 2.
- `add_disponibilidad` / `update_disponibilidad`: quitar el `try/commit`/`except/rollback` propio
  (`cancha_model.py:103-107` y `116-120`); deben convertirse en métodos internos que solo ejecutan SQL
  recibiendo `connection`.
- `delete_disponibilidad`: conservar la semántica de **no commit** y de retornar `rowcount`
  (`cancha_model.py:125`).

### Paso 4 — Reestructurar `reservar_cancha()` en `buscar_complejos_view.py`
- Reemplazar el control manual de `rollback()`/`autocommit`/`commit()` sobre
  `cancha_model.db_service.connection` por `with db_service.transaction()`.
- Pasar `connection` a los métodos internos que hoy se invocan (`delete_disponibilidad`, `add_reserva`).
- Eliminar el `cancha_model.db_service.connection.rollback()` que hoy "cierra la transacción implícita
  de SELECT previos" (`buscar_complejos_view.py:268`).

### Paso 5 — Actualizar el punto de arranque (instanciación única)
- Crear **una sola** instancia de `DatabaseService` en el arranque (`main.py` o composición raíz).
- Entregarla a los modelos de la Opción A en el punto en que se construyen (`buscar_complejos_view.py`,
  `canchas_view.py`, etc. — ver call-sites de constructores en §5).

### Paso 6 — Validación del flujo de reserva y de regresión
- Probar reserva exitosa, reserva por filas_eliminadas == 0, y reserva que lanza excepción.
- Verificar atomicidad real: si `crear_reserva` falla, `eliminar_disponibilidad` debe deshacerse.
- Validar que NO quedan métodos internos con `commit`/`rollback` propio ni conexiones propias en
  los archivos de la Opción A.
- Confirmar el freeze sobre los 3 archivos recién al terminar este hito y tras aprobación.

---

## 5. Riesgo de compatibilidad de firmas (insumo para Hito 5.3)

Cualquier cambio de firma en los métodos de la Opción A debe respetar (o migrar) los **call-sites**
existentes. Universo verificado con `Select-String` (evidencia literal en anexo):

### `delete_disponibilidad(...)`
| Ubicación | Tipo | En Opción A |
|---|---|---|
| `cancha_model.py:122` | definición (retorna `rowcount`, sin commit) | ✅ |
| `buscar_complejos_view.py:278` | call-site | ✅ congelado |
| `canchas_view.py:471` (+ commit manual en 472) | call-site | ❌ **FUERA de congelados** ⚠️ |

### `add_disponibilidad(...)`
| Ubicación | Tipo | En Opción A |
|---|---|---|
| `cancha_model.py:97` | definición | ✅ |
| `canchas_view.py:333` | call-site | ❌ **FUERA de congelados** ⚠️ |

### `update_disponibilidad(...)`
| Ubicación | Tipo | En Opción A |
|---|---|---|
| `cancha_model.py:109` | definición | ✅ |
| `canchas_view.py:437` | call-site | ❌ **FUERA de congelados** ⚠️ |

### `add_reserva(...)`
| Ubicación | Tipo | En Opción A |
|---|---|---|
| `reserva_model.py:34` | definición (hace `connection.commit()` en línea 40) | ✅ |
| `buscar_complejos_view.py:284` | call-site | ✅ congelado |

### Constructores
| Constructor | call-sites | En Opción A |
|---|---|---|
| `CanchaModel()` | `buscar_complejos_view.py:24` ; `canchas_view.py:12` | ✅ / ❌ |
| `ReservaModel()` | `buscar_complejos_view.py:25` ; `mis_reclamos_view.py:17` ; `mis_reservas_view.py:9` | ✅ / ❌ / ❌ |

### ⚠️ Consecuencia de los call-sites fuera de Opción A
`canchas_view.py` depende de `delete_disponibilidad`, `add_disponibilidad` y `update_disponibilidad`
y de `cancha_model.db_service.connection.commit()` (línea 472). Si en Hito 5.3 cambia la firma de estos
métodos (p. ej. exigen `connection` como parámetro obligatorio) y `canchas_view.py` **no se actualiza**,
ese call-site se romperá. Dado que `canchas_view.py` queda en el **Hito 5.3-bis** (backlog), se requiere
una de estas opciones dentro del Paso 6:
1. Conservar un valor por defecto/firma compatible en los métodos migrados (p. ej. `connection=None`)
   para no romper `canchas_view.py`, **o**
2. Aceptar el rompimiento transitorio y coordinar que `canchas_view.py` (Hito 5.3-bis) se actualice en
   la misma entrega antes de levantar el freeze de la vista.

**Decisión:** el riesgo de firma se documenta como pendiente de resolver en Hito 5.3 sin romper
`canchas_view.py` (Hito 5.3-bis); la compatibilidad de firma se confirma como parte del criterio de salida.

---

## 6. Alcance de implementación (Hito 5.3) — Opción A acotada

Queda **acotado** a:
- `reserva_model.py`
- `cancha_model.py`
- `buscar_complejos_view.py`

**Queda fuera de este hito** (backlog técnico → Hito 5.3-bis):
- `canchas_view.py`
- `complejos_view.py`
- `mis_reservas_view.py`
- `mis_reclamos_view.py`
- `gestion_reclamos_view.py`
- `mis_datos_view.py`
- `login_viewmodel.py`
- modelos no involucrados en reserva (`complejo_model.py`, `reclamo_model.py`, `usuario_model.py`)

Los call-sites fuera de Opción A identificados en §5 confirman que `canchas_view.py`
(`delete_disponibilidad:471`, `add_disponibilidad:333`, `update_disponibilidad:437`) y los
constructores en `mis_reclamos_view.py:17` y `mis_reservas_view.py:9` pertenecen al backlog 5.3-bis.

---

## 7. Freeze vigente

- **No modificar** `reserva_model.py`, `cancha_model.py` ni `buscar_complejos_view.py`
  hasta que el diseño quede formalmente aprobado **y** se levante el freeze.
- Esta tarea/documento **NO levanta** el freeze por sí mismo.
- El freeze se levantará recién al iniciar Hito 5.3 o según se apruebe explícitamente.

---

## Anexo — Verificación con evidencia (comandos `Select-String`)

Fragmentos citados en la revisión crítica previa, verificados con números de línea reales:

1. **`reserva_model.py` — commit interno de `add_reserva`:**
   - Firma `add_reserva`: línea **34**.
   - `self.db_service.connection.commit()` dentro de `add_reserva`: línea **40**. ✅ CONFIRMADO.
   - (El resto de métodos de `reserva_model.py` también hacen commit: 49, 54, 63.)

2. **`cancha_model.py` — commit/rollback en los 3 métodos de disponibilidad:**
   - `add_disponibilidad`: firma **97**, commit **104**, rollback **106** (try/except propio). ✅ CONFIRMADO.
   - `update_disponibilidad`: firma **109**, commit **117**, rollback **119**. ✅ CONFIRMADO.
   - `delete_disponibilidad`: firma **122**, retorna `rowcount` en **125**, sin commit. ✅ CONFIRMADO.

3. **`buscar_complejos_view.py` — doble conexión en `reservar_cancha`:**
   - `reservar_cancha`: firma **250**. ✅ CONFIRMADO.
   - Controla `rollback`/`autocommit`/`commit` sobre `cancha_model.db_service.connection`:
     rollback **268**, autocommit False **271-273**, commit **292**, autocommit True **293-295**,
     rollback **319**, rollback **345**. ✅ CONFIRMADO.
   - Comentario «Cerrar cualquier transacción implícita abierta por consultas SELECT previas»: **266-267**.
   - `reserva_model.add_reserva(...)`: **284** → hace commit interno en la conexión de `reserva_model`
     (línea 40 de `reserva_model.py`). **Dos conexiones distintas en el mismo flujo.** ✅ CONFIRMADO.

4. **`canchas_view.py` — commit manual tras `delete_disponibilidad`:**
   - `filas_eliminadas = cancha_model.delete_disponibilidad(...)`: línea **471**.
   - `cancha_model.db_service.connection.commit()`: línea **472**. ✅ CONFIRMADO.
   - **Corrección (número de línea):** la revisión crítica previa citó «canchas_view.py:382-386»;
     la evidencia real ubica este bloque en **471-472**. Se registra como corrección explícita.

### Correcciones explícitas a la revisión previa (números de línea)
- `cancha_model.py`: la revisión previa citó «169-196» para `add_disponibilidad`/`update_disponibilidad`
  y «199-201» para `delete_disponibilidad`. Con `Select-String` los números reales son **97/104/106**,
  **109/117/119** y **122/125**. La evidencia no cambia los hallazgos (R2 y R3 se confirman), solo la
  línea citada, que ahora queda corregida.
- `canchas_view.py`: la revisión previa citó «382-386»; el bloque real está en **471-472**.
  El hallazgo (D2: segundo call-site de `delete_disponibilidad` fuera de congelados) se mantiene.
- `buscar_complejos_view.py`: la revisión previa citó «218-344» como rango amplio del bloque
  `reservar_cancha`; la definición está en **250** y el rango operativo va hasta ~**354**.
  La referencia queda precisada.
