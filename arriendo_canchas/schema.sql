-- ============================================================
-- schema.sql — ArriendoCanchas
-- Generado a partir del código fuente real (Python + Flet + MVVM)
-- Rama: develop | Commit: 78366d4
-- Hito 1 — Fase 4: reconstrucción del esquema local (schema.sql)
-- ============================================================
-- Uso:
--   psql -U postgres -d arriendocanchas_local -f schema.sql
-- ============================================================

-- ============================================================
-- TABLA: Usuarios
-- Extraída de: models/usuario_model.py, views/authenticated/*.py
-- ============================================================
CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario          SERIAL PRIMARY KEY,
    rut                 VARCHAR(20),
    nombre              VARCHAR(100) NOT NULL,
    apellido_paterno    VARCHAR(100),
    apellido_materno    VARCHAR(100),
    telefono            VARCHAR(20),
    correo              VARCHAR(100) NOT NULL UNIQUE,
    contrasena          TEXT NOT NULL,   -- Hash bcrypt generado por passlib (no usa pgcrypto)
    tipo_cuenta         VARCHAR(50) NOT NULL
                        CHECK (tipo_cuenta IN (
                            'MasterAdmin',
                            'Administrador',
                            'ClienteArrendador',
                            'CoordinadorPersonal',
                            'EmpleadoAtencion',
                            'Usuario'
                        )),
    id_admin_responsable INTEGER REFERENCES Usuarios(id_usuario)
);

-- ============================================================
-- TABLA: ComplejosDeportivos
-- Extraída de: models/complejo_model.py
-- Campos verificados:
--   - id_complejo, nombre_complejo, direccion, id_usuario (FK)
--   - telefono, correo, id_imagen, cantidad_canchas (en add_complejo)
-- NOTA: id_imagen es INT NULL sin FK porque NO existe una tabla
-- Imagenes en el código actual. Verificado: ningún archivo en
-- models/, views/, viewmodels/, services/ referencia tabla Imagenes
-- o modelo de imágenes. Se conserva para compatibilidad futura.
-- ============================================================
CREATE TABLE IF NOT EXISTS ComplejosDeportivos (
    id_complejo         SERIAL PRIMARY KEY,
    nombre_complejo     VARCHAR(150) NOT NULL,
    direccion           TEXT NOT NULL,
    id_usuario          INTEGER NOT NULL REFERENCES Usuarios(id_usuario),
    telefono            VARCHAR(20),
    correo              VARCHAR(100),
    id_imagen           INTEGER,  -- Sin FK: no existe tabla Imagenes en el código actual, verificado en models/complejo_model.py, models/cancha_model.py
    cantidad_canchas    INTEGER DEFAULT 0
);

-- ============================================================
-- TABLA: Canchas
-- Extraída de: models/cancha_model.py
-- fecha_disponibilidad: Se mantiene porque el modelo (cancha_model.py)
--   la referencia en add_cancha y update_cancha (INSERT/UPDATE reales).
--   Sin embargo, la vista canchas_view.py (SQL directo) NO la incluye.
--   Verificado en: models/cancha_model.py, views/authenticated/canchas_view.py
-- id_imagen: INT NULL sin FK (misma razón que ComplejosDeportivos)
-- ============================================================
CREATE TABLE IF NOT EXISTS Canchas (
    id_cancha           SERIAL PRIMARY KEY,
    nombre_cancha       VARCHAR(150) NOT NULL,
    tipo_cancha         VARCHAR(50),
    id_complejo         INTEGER NOT NULL REFERENCES ComplejosDeportivos(id_complejo),
    fecha_disponibilidad DATE,
    id_imagen           INTEGER   -- Sin FK: no existe tabla Imagenes en el código actual, verificado en models/complejo_model.py, models/cancha_model.py
);

-- ============================================================
-- TABLA: DisponibilidadCanchas
-- Extraída de: models/cancha_model.py (fetch_disponibilidad,
--   add_disponibilidad, update_disponibilidad, delete_disponibilidad)
-- y views/authenticated/usuarios_view.py
-- ============================================================
CREATE TABLE IF NOT EXISTS DisponibilidadCanchas (
    id_disponibilidad   SERIAL PRIMARY KEY,
    id_cancha           INTEGER NOT NULL REFERENCES Canchas(id_cancha),
    fecha               DATE NOT NULL,
    hora_inicio         TIME NOT NULL,
    hora_fin            TIME NOT NULL
);

-- ============================================================
-- TABLA: Reservas
-- Extraída de: models/reserva_model.py
-- Confirmado: add_reserva(ID, id_cancha, fecha, hora_inicio, hora_fin, estado)
-- hora_inicio y hora_fin son NOT NULL y se usan en buscar_complejos_view.py
-- y usuarios_view.py (flujo de reserva con transacción).
-- INCONSISTENCIA DETECTADA: fetch_reservas() y fetch_reserva_by_id()
-- NO seleccionan hora_inicio ni hora_fin en sus SELECT, pero
-- MisReservasView muestra estos campos. No se corrige en este schema
-- (no se modifican archivos .py).
-- ============================================================
CREATE TABLE IF NOT EXISTS Reservas (
    id_reserva          SERIAL PRIMARY KEY,
    id_usuario          INTEGER NOT NULL REFERENCES Usuarios(id_usuario),
    id_cancha           INTEGER NOT NULL REFERENCES Canchas(id_cancha),
    fecha_reserva       DATE NOT NULL,
    hora_inicio         TIME NOT NULL,
    hora_fin            TIME NOT NULL,
    estado              VARCHAR(50) DEFAULT 'Confirmada'
);

-- ============================================================
-- TABLA: Reclamos
-- Extraída de: models/reclamo_model.py
-- Confirmado: add_reclamo usa INSERT con id_reserva, rut_cliente,
-- tipo_reclamo. Estado con DEFAULT 'Pendiente'.
-- ============================================================
CREATE TABLE IF NOT EXISTS Reclamos (
    id_reclamo          SERIAL PRIMARY KEY,
    id_reserva          INTEGER NOT NULL REFERENCES Reservas(id_reserva),
    rut_cliente         VARCHAR(20),
    tipo_reclamo        VARCHAR(255) NOT NULL,
    estado              VARCHAR(50) DEFAULT 'Pendiente'
);

-- ============================================================
-- Notas sobre inconsistencias detectadas (solo informativo):
-- 1. fetch_reservas() en reserva_model.py no incluye hora_inicio
--    ni hora_fin en el SELECT, pero MisReservasView los referencia.
-- 2. fetch_reserva_by_id() mismo problema.
-- 3. Login no retorna 'rut', pero mis_reclamos_view.py lo usa.
-- 4. Dos definiciones de add_reserva() — la segunda sobreescribe
--    a la primera (la versión con hora_inicio/hora_fin es la activa).
-- 5. canchas_view.py (SQL directo) no usa fecha_disponibilidad ni
--    id_imagen, aunque el modelo cancha_model.py sí.
-- 6. complejos_view.py (SQL directo) no usa telefono, correo,
--    id_imagen, cantidad_canchas, aunque el modelo complejo_model.py sí.
-- ============================================================
