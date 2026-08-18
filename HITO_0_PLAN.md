# HITO 0: Preparación Controlada del Entorno ✅ COMPLETADO

> **Este hito fue ejecutado exitosamente.** Ver commits:
> - `78366d4` — migración a passlib
> - `8cf3d1a` — variables de entorno
>
> Para el estado actual del proyecto, ver [README.md](./README.md), [ALCANCE_ADAPTACION.md](./ALCANCE_ADAPTACION.md) y [HITO_4_SEGUIMIENTO.md](./HITO_4_SEGUIMIENTO.md).

---

## Plan Técnico Detallado (archivo histórico)

> **Objetivo:** Tener la app corriendo localmente conectada a una base de datos PostgreSQL local (no RDS), con variables de entorno, sin credenciales hardcodeadas, y reemplazando `crypt()` de PostgreSQL por `passlib` (Python puro).
>
> **Regla clave:** No implementar funcionalidades nuevas. Solo preparar el entorno. No borrar archivos todavía. No refactorizar vistas completas. No tocar roles ni navegación todavía.

---

## 1. Archivos que HABRÍA QUE TOCAR

### 1.1 Archivos críticos (cambios obligatorios)

| Archivo | Qué cambiar | Tipo de cambio |
|---|---|---|
| `arriendo_canchas/services/database_service.py` | Reemplazar credenciales hardcodeadas por `os.getenv()`. Recibir esquema por variable de entorno. | ✅ Modificar |
| `arriendo_canchas/models/usuario_model.py` | Reemplazar `crypt(%s, gen_salt('bf'))` por hashing con `passlib` (Python puro). | ✅ Modificar |
| `arriendo_canchas/viewmodels/login_viewmodel.py` | Reemplazar verificación con `crypt()` de PostgreSQL por `passlib.verify()`. | ✅ Modificar |
| `arriendo_canchas/views/authenticated/mis_datos_view.py` | La función `update_usuario_full` usa `crypt()` internamente → se actualiza automáticamente al cambiar el modelo. | ✅ Indirecto |
| `.env` (archivo nuevo) | Crear archivo con variables de entorno para BD local. | 🆕 Crear |
| `.gitignore` | Agregar `.env` a la lista para no versionar credenciales. | ✅ Modificar |

### 1.2 Archivos que crean conexión directa (NO need to change in Hito 0, they use models)

Los siguientes archivos **ya usan los modelos** (`UsuarioModel`, `CanchaModel`, etc.), que a su vez llaman a `DatabaseService`. Cuando modifiquemos `database_service.py`, estos heredarán el cambio automáticamente:

- `arriendo_canchas/models/complejo_model.py` — usa `DatabaseService()` → hereda cambio
- `arriendo_canchas/models/cancha_model.py` — usa `DatabaseService()` → hereda cambio
- `arriendo_canchas/models/reserva_model.py` — usa `DatabaseService()` → hereda cambio
- `arriendo_canchas/models/reclamo_model.py` — usa `DatabaseService()` → hereda cambio
- `arriendo_canchas/viewmodels/login_viewmodel.py` — usa `DatabaseService()` directamente (sí tocar)

### 1.3 Archivos que abren DB directa (¡CUIDADO!)

| Archivo | Patrón actual | Riesgo |
|---|---|---|
| `arriendo_canchas/views/authenticated/complejos_view.py` | Crea `DatabaseService()` + `cursor` propio + queries SQL dirty | 🔴 **ALTO** — No usa modelo, hace queries directo |
| `arriendo_canchas/views/authenticated/canchas_view.py` | Crea `DatabaseService()` + `cursor` + queries SQL dirty | 🔴 **ALTO** — No usa modelo, hace queries directo |
| `arriendo_canchas/views/authenticated/buscar_complejos_view.py` | Usa modelos pero hace 1 query directa (en `ver_canchas`) | 🟡 MEDIO |
| `arriendo_canchas/views/authenticated/usuarios_view.py` | Usa `cancha_model.cursor.execute()` directo | 🟡 MEDIO |

**Decisión para Hito 0:** Estos archivos **NO se refactorizarán** en este hito (violaría "no refactorizar vistas completas"). En su lugar, la conexión que abren seguirá funcionando porque el cambio en `database_service.py` será transparente (solo cambia cómo se conecta, no la interfaz).

---

## 2. Archivos que NO se deben tocar todavía

| Archivo | Motivo |
|---|---|
| `arriendo_canchas/main.py` | Tiene toda la lógica de roles (6 tipos). Se refactoriza en Hito 1+ |
| `arriendo_canchas/views/widgets/sidebar.py` | Tiene lógica de 6 roles. Se reduce en Hito 1+ |
| `arriendo_canchas/views/authenticated/complejos_view.py` | Usa DB directa pero no se refactoriza vista en este hito |
| `arriendo_canchas/views/authenticated/canchas_view.py` | Idem |
| `arriendo_canchas/views/authenticated/buscar_complejos_view.py` | Idem (solo cambios indirectos) |
| `arriendo_canchas/views/authenticated/usuarios_view.py` | Idem |
| `arriendo_canchas/views/authenticated/mis_reservas_view.py` | Funciona sin cambios |
| `arriendo_canchas/views/authenticated/mis_reclamos_view.py` | Funciona sin cambios (opcional) |
| `arriendo_canchas/views/authenticated/admin_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/master_admin_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/cliente_arrendador_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/coordinador_personal_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/empleado_atencion_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/usuario_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/administradores_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/arrendadores_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/coordinadores_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/atencion_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/authenticated/base_user_view.py` | Se descartará en Hito 1+ |
| `arriendo_canchas/views/home_view.py` | No tocar (funciona) |
| `arriendo_canchas/views/login_view.py` | No tocar (usa `LoginViewModel` que modificaremos) |
| `arriendo_canchas/views/widgets/navbar.py` | No tocar |
| `arriendo_canchas/views/widgets/navbar_pages.py` | No tocar |
| `arriendo_canchas/viewmodels/user_viewmodel.py` | No tocar (funciona) |
| `arriendo_canchas/viewmodels/register_viewmodel.py` | Vacío, pero no tocar (se creará en Hito 1+) |
| `arriendo_canchas/viewmodels/main_viewmodel.py` | Vacío, no tocar |
| `arriendo_canchas/services/auth_service.py` | Vacío, no tocar |
| `rutas.py` | Script auxiliar, no tocar |
| `estructura_proyecto.txt` | Obsoleto, no tocar |

---

## 3. Variables de Entorno Necesarias

Se creará un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# === Base de Datos PostgreSQL Local ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=arriendocanchas_local
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=public
```

Variables que se usarán en `database_service.py`:

| Variable | Propósito | Valor por defecto (desarrollo local) |
|---|---|---|
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto | `5432` |
| `DB_NAME` | Nombre de la base de datos | `arriendocanchas_local` |
| `DB_USER` | Usuario de BD | `postgres` (el de la instalación local) |
| `DB_PASSWORD` | Contraseña | `postgres` (la que se configure localmente) |
| `DB_SCHEMA` | Schema a usar | `public` (cambiar si se usa otro) |

**IMPORTANTE:** `.env` NUNCA debe subirse al repositorio. Se agregará a `.gitignore`.

---

## 4. Dependencias Mínimas Reales

### Lo que ya está en `requirements.txt` (instalado)

El archivo `arriendo_canchas/requirements.txt` ya contiene TODO lo necesario:

| Dependencia | Versión | Uso |
|---|---|---|
| `flet==0.24.1` | ✓ | Framework UI |
| `flet-runtime==0.24.1` | ✓ | Runtime de Flet |
| `psycopg2-binary==2.9.10` | ✓ | Conector PostgreSQL |
| `passlib==1.7.4` | ✅ **Ya incluido** | Hashing de contraseñas Python puro |
| `python-dotenv==1.0.1` | ✅ **Ya incluido** | Variables de entorno desde `.env` |
| `fastapi==0.115.3` | ✓ (dependencia de Flet) | Servidor web de Flet |
| `uvicorn==0.32.0` | ✓ (dependencia de Flet) | Servidor ASGI |

### No es necesario instalar nada adicional

`passlib` y `python-dotenv` **ya están en el requirements.txt**. Solo hay que asegurarse de que estén instaladas en el entorno virtual.

### Lo que sobra (se puede ignorar por ahora)

El requirements.txt tiene muchas dependencias traídas por Flet y psycopg2. No hay que limpiarlas en este hito.

---

## 5. Estrategia para PostgreSQL Local

### Paso a paso para crear la BD local

1. **Verificar que PostgreSQL esté instalado localmente**
   ```bash
   psql --version
   ```
   Si no está instalado, instalar PostgreSQL (https://www.postgresql.org/download/).

2. **Crear la base de datos**
   ```bash
   createdb -U postgres arriendocanchas_local
   ```
   O desde psql:
   ```sql
   CREATE DATABASE arriendocanchas_local;
   ```

3. **Crear el schema SQL**

   Se creará un archivo `arriendo_canchas/schema.sql` con las tablas necesarias. Basado en el código existente, las tablas son:
   - `Usuarios` (con columna `contrasena` como TEXT en vez de usar crypt)
   - `ComplejosDeportivos`
   - `Canchas`
   - `DisponibilidadCanchas`
   - `Reservas`
   - `Reclamos` (opcional, para mantener compatibilidad)

4. **Ejecutar el schema**
   ```bash
   psql -U postgres -d arriendocanchas_local -f arriendo_canchas/schema.sql
   ```

5. **Crear un usuario semilla** (admin local para pruebas)
   ```sql
   INSERT INTO Usuarios (nombre, correo, contrasena, tipo_cuenta)
   VALUES ('Admin Local', 'admin@local.com', '<hash_generado_con_passlib>', 'Administrador');
   ```

### Consideraciones

- **NO se usará el esquema `arrcanchasdb`** (era del RDS original). Se usará el schema `public` (o uno propio como `local`).
- Las tablas se crean con tipos estándar PostgreSQL (TEXT, INTEGER, DATE, TIME, etc.)
- La columna `contrasena` almacenará el hash de passlib (formato bcrypt `$2b$...`).

---

## 6. Estrategia para Reemplazar `crypt()` por `passlib`

### ¿Qué hace `crypt()` actualmente?

En PostgreSQL, la función `crypt()` de `pgcrypto` genera un hash bcrypt con sal:
```sql
crypt('contraseña', gen_salt('bf'))  -- genera algo como $2a$08$...
```

Y verifica:
```sql
SELECT crypt('contraseña', hashed_password) = hashed_password
```

### ¿Qué haremos con `passlib`?

`passlib` es una biblioteca Python pura que implementa el mismo algoritmo bcrypt. El flujo será:

#### En `usuario_model.py` (crear/actualizar usuario):

**Antes (SQL):**
```python
INSERT INTO Usuarios ... VALUES (..., crypt(%s, gen_salt('bf')), ...)
```

**Después (Python):**
```python
from passlib.hash import bcrypt
hashed_password = bcrypt.hash(contrasena)
# Luego: INSERT INTO ... VALUES (..., %s, ...) con hashed_password
```

#### En `login_viewmodel.py` (verificar login):

**Antes (SQL):**
```python
verify_query = "SELECT crypt(%s, %s) = %s AS password_match"
```

**Después (Python):**
```python
from passlib.hash import bcrypt
bcrypt.verify(contrasena_plana, hashed_password_de_la_db)
```

#### Funciones afectadas en `usuario_model.py`:

| Método | Línea | Cambio |
|---|---|---|
| `add_usuario` | `crypt(%s, gen_salt('bf'))` | Reemplazar por `bcrypt.hash()` en Python |
| `update_usuario_full` | `crypt(%s, gen_salt('bf'))` | Reemplazar por `bcrypt.hash()` en Python |

#### Cambio en el schema de BD:

La columna `contrasena` pasará de depender de `crypt()` a almacenar texto plano del hash:
```sql
contrasena TEXT NOT NULL  -- almacenará el hash bcrypt generado por passlib
```

(No hay cambio de tipo, ya que `crypt()` ya devuelve TEXT, pero conceptualmente se rompe la dependencia de pgcrypto.)

---

## 7. Riesgos Antes de Ejecutar Cambios

### 🔴 Riesgos Altos

| # | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| 1 | **PostgreSQL no instalado localmente** | No se puede probar la app | Verificar con `psql --version` antes. Si no está, instalar PostgreSQL 15+. |
| 2 | **passlib ya incluido pero no se usó en el proyecto original** | Bajo realmente, porque ya está en requirements | Solo asegurarse de hacer `pip install -r requirements.txt` |
| 3 | **Queries directas en vistas** (complejos_view, canchas_view) usan `cursor` propio que depende de `DatabaseService()` | Si la conexión falla, esas vistas también fallan | El cambio en `database_service.py` solo afecta la conexión, no el cursor. Si la BD local está funcionando, las vistas heredan el cambio sin problema. |
| 4 | **El schema `arrcanchasdb` está hardcodeado en `search_path` de database_service.py** | Si no existe el esquema, la conexión falla | Cambiar a `public` (o configurable por `DB_SCHEMA`). |

### 🟡 Riesgos Medios

| # | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| 5 | **Las vistas autenticadas esperan 6 roles (tipo_cuenta)** | Si el usuario semilla tiene un tipo_cuenta no esperado, no se renderizan bien | Crear usuario semilla con tipo_cuenta que coincida con los existentes (p.ej. "Administrador" o "ClienteArrendador") |
| 6 | **La tabla `Usuarios` puede tener restricciones NOT NULL** (como `rut`, `apellido_paterno`) | Podría fallar al insertar usuario de prueba | En el schema, hacer opcionales esos campos o proveer valores dummy |
| 7 | **passlib puede requerir `bcrypt` system library** | En Windows puede dar error si no hay compilador C | La dependencia `bcrypt` (no `bcrypt`) se instala como wheel si usamos `pip install passlib[bcrypt]`. En requirements ya está `passlib==1.7.4`; si da error, instalar también `bcrypt` como paquete pip. |
| 8 | **Flet 0.24.1 puede tener incompatibilidad con Python 3.13** | Error al importar flet | Verificar versión de Python (3.10, 3.11 o 3.12 recomendadas). Usar `pyenv` o `conda` para gestionar versión. |

### 🟢 Riesgos Bajos

| # | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| 9 | **Los modelos tienen `close()` manual** | No se cierran conexiones correctamente en caso de error | Es un tema de diseño (no se toca en Hito 0) |
| 10 | **python-dotenv no carga `.env` por defecto** | Las variables no estarán disponibles | Agregar `load_dotenv()` al inicio de `database_service.py` |

---

## 8. Orden Recomendado de Implementación

Cada paso debe ser validado antes de continuar.

### Paso 1: Preparar PostgreSQL Local
- Verificar que PostgreSQL esté instalado
- Crear la base de datos `arriendocanchas_local`
- Crear el schema con las tablas necesarias (`schema.sql`)

### Paso 2: Crear `.env` con credenciales locales
- Crear archivo `.env` en raíz del proyecto
- Agregar `.env` a `.gitignore`

### Paso 3: Modificar `database_service.py`
- Reemplazar credenciales hardcodeadas por `os.getenv()`
- Agregar `load_dotenv()` al inicio
- Cambiar `search_path` a configurable (`DB_SCHEMA`)
- **No cambiar la interfaz** (sigue teniendo `connection`, `cursor`, `close()`)

### Paso 4: Modificar `usuario_model.py`
- Importar `passlib.hash import bcrypt`
- Reemplazar `crypt(%s, gen_salt('bf'))` en `add_usuario` por `bcrypt.hash(contrasena)` + parámetro SQL
- Reemplazar en `update_usuario_full` de igual forma
- El método `fetch_usuarios` y `fetch_usuario_by_id` no cambian

### Paso 5: Modificar `login_viewmodel.py`
- Importar `passlib.hash import bcrypt`
- Reemplazar verificación SQL con `bcrypt.verify(contrasena, hashed_password)`
- Mantener el resto de la lógica igual

### Paso 6: Crear usuario semilla
- Insertar un usuario admin en la BD local (contraseña hasheada con passlib)
- Verificar que login funciona

### Paso 7: Probar la app
- `cd arriendo_canchas && python main.py`
- Verificar que carga la landing page
- Probar login con usuario semilla
- Verificar que las vistas cargan (aunque algunas puedan fallar por roles)

### Paso 8: Validar criterio de éxito
- ✅ `python main.py` abre en `http://localhost:8555`
- ✅ Landing page se ve correctamente
- ✅ Login con usuario semilla funciona
- ✅ Vista de complejos/canchas (si el rol lo permite) cargan sin errores de BD
- ✅ No hay credenciales hardcodeadas en el código
- ✅ El `.env` no está versionado en git

---

## Resumen de cambios (estimación)

| Archivo | Cambio | Líneas aprox. |
|---|---|---|
| `services/database_service.py` | Reemplazar hardcode por `os.getenv()` + `load_dotenv()` | ~10 |
| `models/usuario_model.py` | Reemplazar `crypt()` por `bcrypt.hash()` | ~6 |
| `viewmodels/login_viewmodel.py` | Reemplazar `crypt()` por `bcrypt.verify()` | ~8 |
| `.env` (nuevo) | Variables de entorno | ~7 |
| `.gitignore` | Agregar `.env` | ~1 |
| `schema.sql` (nuevo) | Creación de tablas | ~70 |

**Total estimado: ~100 líneas nuevas/modificadas (sin contar schema.sql).**

---

## Checklist de verificación pre-ejecución

- [ ] PostgreSQL instalado y funcionando
- [ ] Base de datos `arriendocanchas_local` creada
- [ ] Schema SQL revisado y listo
- [ ] `passlib` presente en requirements.txt (✓ ya lo está)
- [ ] `python-dotenv` presente en requirements.txt (✓ ya lo está)
- [ ] Python 3.10-3.12 verificado (no 3.13)
- [ ] Entorno virtual creado y activado
- [ ] `pip install -r arriendo_canchas/requirements.txt` ejecutado

---

*Fin del plan HITO 0*
