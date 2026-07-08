# ALCANCE_ADAPTACION.md

## Proyecto: ArriendoCanchas — Versión Personal

---

## 1. Objetivo nuevo del proyecto

Crear una **versión propia y deployable** de una plataforma de arriendo de canchas deportivas, tomando como base el repositorio heredado `arriendocanchas`.

**El proyecto original no se continuará.** Este es un fork personal autorizado que adapta el código existente para construir una aplicación funcional, desplegable en hosting económico, idealmente orientada a un solo arrendador dueño de complejos deportivos (no multi-tenant con roles complejos como el original).

**Meta final:** Una app web funcional donde:
- Un administrador gestiona sus complejos, canchas y disponibilidad.
- Usuarios (clientes) se registran, buscan canchas disponibles y reservan.
- Todo desplegado en Render o Railway con PostgreSQL.

---

## 2. Qué partes del proyecto heredado se pueden reutilizar

### Código directamente reutilizable (con adaptaciones menores)

| Archivo | Estado | Uso esperado |
|---|---|---|
| `models/cancha_model.py` | CRUD completo + disponibilidad | Reutilizar con mínimos cambios |
| `models/complejo_model.py` | CRUD completo + búsqueda ILIKE | Reutilizar |
| `models/reserva_model.py` | CRUD completo | Reutilizar |
| `models/reclamo_model.py` | Consulta e inserción | Reutilizar (opcional) |
| `models/usuario_model.py` | CRUD completo con `crypt()` | Reutilizar cambiando hashing |
| `viewmodels/login_viewmodel.py` | Lógica de login funcional | Reutilizar adaptando hashing |
| `viewmodels/user_viewmodel.py` | State holder simple | Reutilizar tal cual |
| `views/login_view.py` | Formulario login funcional | Reutilizar |
| `views/authenticated/canchas_view.py` | CRUD canchas + disponibilidad completo | Reutilizar |
| `views/authenticated/complejos_view.py` | CRUD complejos completo | Reutilizar |
| `views/authenticated/mis_datos_view.py` | Editar perfil | Reutilizar |
| `views/authenticated/mis_reservas_view.py` | Listar/cancelar reservas | Reutilizar |
| `views/authenticated/mis_reclamos_view.py` | Listar/crear reclamos | Reutilizar (opcional) |
| `views/authenticated/buscar_complejos_view.py` | Búsqueda + reserva | Reutilizar |
| `views/authenticated/usuarios_view.py` | Mal nombrado pero funcional (reserva por fecha) | Reutilizar renombrando |
| `views/home_view.py` | Landing multi-sección | Reutilizar |
| `views/widgets/navbar.py` | Navbar landing | Reutilizar |
| `views/widgets/navbar_pages.py` | Navbar autenticado | Reutilizar |
| `views/widgets/sidebar.py` | Menú por rol | **Reducir** (solo 2 roles) |
| `views/who_we_are_view.py` | Texto estático | Reutilizar o modificar |
| `views/services_view.py` | Tarjetas decorativas | Reutilizar |
| `views/our_clients_view.py` | Placeholder | Reutilizar |
| `views/contact_us_view.py` | Formulario (sin envío real) | Reutilizar (conectar a algo) |
| `main.py` | Routing + lógica de roles | **Reescribir parcialmente** |

### Lógica de negocio reutilizable

- Flujo completo de **búsqueda → disponibilidad → reserva** (joya del proyecto original).
- Patrón **Model → ViewModel → View** (aunque no es MVVM puro, es consistente).
- Nomenclatura de tablas y campos (base para crear un schema nuevo).

---

## 3. Qué partes conviene descartar o dejar fuera

| Componente | Decisión | Motivo |
|---|---|---|
| Sistema multi-rol (6 tipos de cuenta) | ❌ Descartar | El proyecto original tenía MasterAdmin, Admin, ClienteArrendador, CoordinadorPersonal, EmpleadoAtencion, Usuario. Para una versión personal bastan **2 roles**: `admin` (dueño/complejo) y `usuario` (cliente). |
| `views/authenticated/admin_view.py` | ❌ Descartar | Esqueleto vacío, irrelevante sin multi-rol |
| `views/authenticated/master_admin_view.py` | ❌ Descartar | Idem |
| `views/authenticated/cliente_arrendador_view.py` | ❌ Descartar | Idem |
| `views/authenticated/coordinador_personal_view.py` | ❌ Descartar | Idem |
| `views/authenticated/empleado_atencion_view.py` | ❌ Descartar | Idem |
| `views/authenticated/usuario_view.py` | ❌ Descartar | Idem |
| `views/authenticated/base_user_view.py` | ❌ Descartar | No se usa en routing |
| `views/authenticated/administradores_view.py` | ❌ Descartar | CRUD de administración de usuarios (innecesario sin multi-rol) |
| `views/authenticated/arrendadores_view.py` | ❌ Descartar | Idem |
| `views/authenticated/coordinadores_view.py` | ❌ Descartar | Idem |
| `views/authenticated/atencion_view.py` | ❌ Descartar | Idem |
| `viewmodels/main_viewmodel.py` | ❌ Descartar | Archivo vacío |
| `viewmodels/register_viewmodel.py` | ❌ Reescribir | Vacío, pero necesario crear registro de usuarios |
| `services/auth_service.py` | ❌ Reescribir | Vacío, pero útil como módulo separado |
| `models/reclamo_model.py` | ⚠️ Opcional | Funcionalidad secundaria; se puede agregar después |
| `views/authenticated/mis_reclamos_view.py` | ⚠️ Opcional | Idem |
| `assets/client_logos/` | ❌ No existe en disco | Si se quiere, crear después |
| `rutas.py` | ❌ Descartar | Script auxiliar del autor original, no parte del proyecto |
| `estructura_proyecto.txt` | ❌ Descartar | Obsoleto, caracteres rotos |

---

## 4. Riesgos de mantener Flet como tecnología principal

### Riesgos identificados

| Riesgo | Nivel | Detalle |
|---|---|---|
| Flet no es estándar web | 🔴 Alto | Flet genera una app web a través de un servidor FastAPI + WebSockets. No es una SPA tradicional ni HTML estático. Pocos hosts soportan esto de manera simple. |
| Dependencia de `flet.app()` | 🔴 Alto | La app se lanza con `flet.app(target=main, view="web_browser")`. En Render/Railway, requeriría mantener un proceso largo corriendo (no es serverless friendly). |
| Flet 0.24.1 | 🟡 Medio | Versión relativamente reciente pero el ecosistema cambia rápido. Podría haber breaking changes. |
| App híbrida (no es web nativa) | 🟡 Medio | Flet renderiza en un canvas/webview. No es SEO-friendly. Para una app de gestión interna no es problema, pero para un sitio público limita visibilidad. |
| WebSockets persistentes | 🟡 Medio | Flet usa WebSockets para comunicación bidireccional. Puede ser bloqueado por firewalls/proxies corporativos. |
| Renderizado server-side | 🟡 Medio | La interfaz se renderiza en el servidor y se envía al cliente. Mayor consumo de RAM/CPU comparado con una SPA moderna. |
| Comunidad pequeña | 🟡 Medio | Comparado con Django+React o Flask+Vue, la comunidad de Flet es mucho más pequeña. |

### Pero también hay ventajas

| Ventaja | Detalle |
|---|---|
| Código 100% Python | No necesitas JavaScript. Si solo sabes Python, es ideal. |
| Prototipado rápido | Con pocas líneas tienes UI funcional con DataTables, formularios, navegación. |
| Estado compartido simple | El objeto `page` mantiene estado global sin necesidad de Redux/Vuex. |
| Ya tenemos el 80% del frontend | Las vistas ya están escritas en Flet. Migrar a React/Vue significaría reescribir todo. |

---

## 5. Riesgos de depender de AWS RDS hardcodeado

| Riesgo | Nivel | Detalle |
|---|---|---|
| BD externa puede no existir | 🔴 Alto | El `host` apunta a un RDS del creador original. Si la instancia fue eliminada o las credenciales cambiaron, la app no funciona en absoluto. |
| Credenciales en texto plano | 🔴 Alto | `user='postgres'`, `password='aRRCANCHAS24'` están hardcodeados. Esto es una violación de seguridad grave si el repo es público. |
| Esquema `arrcanchasdb` | 🟡 Medio | El search_path apunta a un esquema específico. Si no existe, la conexión falla aunque el host responda. |
| Función `crypt()` de PostgreSQL | 🔴 Alto | Toda la autenticación y creación de usuarios depende de la función `crypt()` de PostgreSQL (pgcrypto). Si migras a SQLite o MySQL, el hashing de contraseñas debe reescribirse completamente. |
| Sin variables de entorno | 🔴 Alto | No hay uso de `.env` ni `os.getenv()`. Todo está fijo. Para producción, las credenciales deben ir en variables de entorno, no en código. |
| Sin pool de conexiones | 🟡 Medio | Cada ViewModel/Model crea una nueva conexión `psycopg2` y la cierra. En producción con múltiples usuarios, esto saturará la BD. |

---

## 6. Alternativas de hosting

### 6.1 Render

| Ítem | Detalle |
|---|---|
| Tipo | PaaS (Platform as a Service) |
| Soporte para Flet | 🟡 Parcial. Render soporta procesos largos (Web Service), que es lo que Flet necesita. Pero Flet no está en su stack oficial. |
| Base de datos | PostgreSQL gratis (hasta 1 GB). |
| Precio | $0/mes (Web Service gratuito duerme a los 15 min de inactividad). BD gratis por 90 días. |
| Deploy | Git push + Dockerfile o runtime Python. |
| Requisitos extra | Necesitas un `Dockerfile` o configurar `render.yaml`. La app debe estar configurada para correr como proceso web escuchando en 0.0.0.0:$PORT. |
| Limitaciones | Web Service gratis se duerme. Tarda ~30s en despertar. No es ideal para demo pública, pero aceptable para desarrollo. |
| Veredicto | 🟢 **Opción principal recomendada.** Buena relación entre costo, facilidad y PostgreSQL incluida. |

### 6.2 Railway

| Ítem | Detalle |
|---|---|
| Tipo | PaaS |
| Soporte para Flet | 🟡 Parcial. Railway también soporta procesos largos. Similar a Render. |
| Base de datos | PostgreSQL nativo. |
| Precio | ~$5/mes después del crédito inicial ($5 gratis). Modelo de pago por uso. |
| Deploy | Git push + detección automática de runtime Python. |
| Requisitos extra | Similar a Render: la app debe escuchar en `0.0.0.0:$PORT`. |
| Limitaciones | Ya no tiene tier gratis ilimitado (desde 2024). Para un proyecto personal de bajo costo puede funcionar. |
| Veredicto | 🟢 **Alternativa sólida a Render.** Buena si el crédito inicial alcanza. |

### 6.3 Vercel

| Ítem | Detalle |
|---|---|
| Tipo | Serverless + Edge Functions |
| Soporte para Flet | ❌ **No compatible.** Vercel está diseñado para serverless (funciones que arrancan, responden y mueren). Flet requiere un proceso **persistente** (WebSocket + UI continua). |
| Base de datos | No tiene BD nativa. Usarías Neon o Supabase como complemento. |
| Precio | Gratis para proyectos personales. |
| Deploy | Next.js, SPA estáticas, Serverless Functions. Flet no encaja en ningún adaptador de Vercel. |
| Veredicto | 🔴 **Descartado para Flet.** Solo viable si migras a una arquitectura completamente diferente (FastAPI + React/Vue). |

### 6.4 Local / Demo

| Ítem | Detalle |
|---|---|
| Tipo | Ejecución local o red local |
| Soporte para Flet | Nativo. `flet.app(target=main, view="web_browser")` abre el navegador local. |
| Base de datos | PostgreSQL local (instalado manualmente) o SQLite (con adaptación del código). |
| Precio | $0 |
| Deploy | `python main.py` y listo. |
| Limitaciones | Solo visible en tu máquina (o red LAN). No es accesible desde internet sin túneles (ngrok, Cloudflare Tunnel). |
| Veredicto | 🟢 **Ideal para desarrollo y pruebas locales.** No apto para producción pública. |

---

## 7. Recomendación técnica final de hosting

### Decisión: **Flet + PostgreSQL en Render**

**Razones:**

1. **Flet funciona como proceso largo** — Render (Web Service) y Railway soportan esto de forma nativa. Vercel no.
2. **PostgreSQL incluido** — Render ofrece PostgreSQL gratis (1 GB, 90 días, luego se renueva o se paga).
3. **Sin costo inicial** — El tier gratis de Render permite una demo funcional, aunque con latencia al despertar.
4. **Mínima migración de código** — Solo necesitas:
   - Pasar credenciales a variables de entorno (`os.getenv`).
   - Configurar el puerto dinámico (`$PORT`).
   - Agregar un `Dockerfile` o `render.yaml` simple.
5. **Ruta de escape** — Si Flet no funciona bien en producción, migrar a FastAPI + React manteniendo PostgreSQL en Render.

### Plan alternativo

| Prioridad | Opción | Cuándo elegirla |
|---|---|---|
| 1ª | Render | Para producción MVP |
| 2ª | Railway | Si prefieres Railway o se acaba el tier gratis de Render |
| 3ª | Local + ngrok | Para demos rápidas (sin BD externa) |
| 4ª | Vercel | Solo si abandonas Flet y migras a FastAPI + React |

---

## 8. MVP propuesto para mi versión personal

### Roles (solo 2)

| Rol | Funcionalidades |
|---|---|
| **Admin** (dueño) | Gestiona complejos, canchas, disponibilidad. Ve reservas de sus canchas. |
| **Usuario** (cliente) | Se registra, busca canchas, reserva, ve/cancela sus reservas. |

### Funcionalidades del MVP

| # | Funcionalidad | Prioridad | Origen |
|---|---|---|---|
| 1 | Landing page pública (quienes somos, servicios, contacto) | Alta | Heredado |
| 2 | Registro de usuarios (con contraseña hasheada) | Alta | **Nuevo** (heredado vacío) |
| 3 | Inicio de sesión | Alta | Heredado (adaptar hashing) |
| 4 | CRUD Complejos Deportivos (admin) | Alta | Heredado |
| 5 | CRUD Canchas + Disponibilidad (admin) | Alta | Heredado |
| 6 | Buscar complejos y canchas disponibles (usuario) | Alta | Heredado |
| 7 | Reservar cancha (usuario) | Alta | Heredado |
| 8 | Ver/Cancelar mis reservas (usuario) | Alta | Heredado |
| 9 | Editar mi perfil (usuario) | Media | Heredado |
| 10 | Panel admin con resumen de reservas | Media | **Nuevo** |
| 11 | Formulario de contacto funcional (opcional) | Baja | Heredado (conectar a email) |

### Lo que NO incluye el MVP

- Sistema de reclamos.
- Múltiples roles (Coordinador, Atención, etc.).
- Dashboard con gráficos y métricas.
- Pagos en línea.
- Notificaciones por email.
- Subida de imágenes de canchas/complejos.
- Modo oscuro (ya está en navbar_pages.py pero no es crítico).

---

## 9. Funcionalidades fuera del MVP

| Funcionalidad | Cuándo agregarla | Dependencias |
|---|---|---|
| Sistema de reclamos | Post-MVP (si hay demanda) | Casi listo (heredado) |
| Imágenes para complejos/canchas | Post-MVP | Almacenamiento externo (Cloudinary, S3) |
| Pagos en línea | Post-MVP | Webpay, MercadoPago, Stripe |
| Notificaciones por email | Post-MVP | SendGrid, SMTP |
| Calendario visual de disponibilidad | Post-MVP | Widget de calendario |
| App móvil (Android/iOS) | Post-MVP | Flet permite exportar a móvil, pero requiere re-empaquetar |
| Multi-idioma | Post-MVP | i18n |
| Administración multi-complejo para un admin | Post-MVP | Heredado lo soporta parcialmente |

---

## 10. Primer hito técnico para comenzar

### Hito 0: "La app prende en local"

**Objetivo:** Tener la app corriendo localmente conectada a una base de datos PostgreSQL local (no RDS).

**Pasos (sin implementar aún, solo plan):**

```
1. Crear base de datos PostgreSQL local (ej: "arriendocanchas_local")
2. Diseñar schema SQL mínimo (tablas: usuarios, complejos, canchas, disponibilidad, reservas)
3. Adaptar database_service.py para usar variables de entorno
4. Instalar dependencias (pip install -r requirements.txt)
5. Ejecutar python main.py y verificar que carga
6. Probar login y CRUD básico
```

**Criterio de éxito:** `python main.py` abre la app en `http://localhost:8555`, carga la landing page, permite login (con usuario seed creado en BD local) y muestra los CRUDs funcionales.

---

## Conclusión final

| Dimensión | Decisión |
|---|---|
| **Framework UI** | ✅ **Seguir con Flet** — el frontend ya está escrito, es funcional y coherente. Migrar a otra tecnología (React, Vue) retrasaría el proyecto meses sin valor añadido inmediato. |
| **Base de datos** | ✅ **PostgreSQL** — heredado y robusto. Cambiar la dependencia de `crypt()` a `passlib` (Python puro) para no depender de funciones específicas de PG. |
| **Hosting** | ✅ **Render (Web Service + PostgreSQL)** — mejor equilibrio entre costo, soporte para procesos largos y facilidad de deploy. |
| **Roles** | ✅ **Reducir de 6 a 2** (admin + usuario) — simplifica el 70% del código de routing y vistas. |
| **Arquitectura** | ✅ **Conservar MVVM ligero actual** — no sobreingenierizar. |

### Riesgo principal aceptado

> **Si Flet resulta problemático en Render (latencia, WebSockets, consumo de RAM), la alternativa sería migrar a FastAPI + React manteniendo PostgreSQL en Render, reutilizando solo los modelos y la lógica de negocio.**

Esa decisión se tomará después del Hito 0, cuando tengamos evidencia concreta del comportamiento de Flet en producción.
