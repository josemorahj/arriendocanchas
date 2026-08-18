-- ============================================================
-- seed_disponibilidad_dev.sql
-- Semilla exclusiva para desarrollo.
-- Propósito: Poblar disponibilidades para la cancha existente
-- id_cancha = 1, permitiendo validar el flujo de reservas
-- (Usuario -> buscar complejo -> ver cancha -> ver disponibilidad
--  -> reservar -> reserva creada / disponibilidad eliminada).
--
-- Ubicación: arriendo_canchas/ (mismo directorio que schema.sql)
-- Uso: psql -U postgres -d arriendocanchas -f seed_disponibilidad_dev.sql
--
-- Requisitos:
--   - No modifica schema.sql ni ningún archivo .py
--   - No inserta usuarios, complejos ni canchas
--   - No borra reservas ni reclamos existentes
--   - Es idempotente: no crea duplicados si se ejecuta múltiples veces
-- ============================================================

BEGIN;

-- ============================================================
-- Disponibilidad 1: mañana (CURRENT_DATE + 1) 10:00 a 12:00
-- ============================================================
INSERT INTO DisponibilidadCanchas (id_cancha, fecha, hora_inicio, hora_fin)
SELECT 1, CURRENT_DATE + 1, '10:00:00', '12:00:00'
WHERE NOT EXISTS (
    SELECT 1 FROM DisponibilidadCanchas
    WHERE id_cancha = 1
      AND fecha = CURRENT_DATE + 1
      AND hora_inicio = '10:00:00'
      AND hora_fin = '12:00:00'
);

-- ============================================================
-- Disponibilidad 2: mañana (CURRENT_DATE + 1) 14:00 a 16:00
-- ============================================================
INSERT INTO DisponibilidadCanchas (id_cancha, fecha, hora_inicio, hora_fin)
SELECT 1, CURRENT_DATE + 1, '14:00:00', '16:00:00'
WHERE NOT EXISTS (
    SELECT 1 FROM DisponibilidadCanchas
    WHERE id_cancha = 1
      AND fecha = CURRENT_DATE + 1
      AND hora_inicio = '14:00:00'
      AND hora_fin = '16:00:00'
);

-- ============================================================
-- Disponibilidad 3: pasado mañana (CURRENT_DATE + 2) 09:00 a 11:00
-- ============================================================
INSERT INTO DisponibilidadCanchas (id_cancha, fecha, hora_inicio, hora_fin)
SELECT 1, CURRENT_DATE + 2, '09:00:00', '11:00:00'
WHERE NOT EXISTS (
    SELECT 1 FROM DisponibilidadCanchas
    WHERE id_cancha = 1
      AND fecha = CURRENT_DATE + 2
      AND hora_inicio = '09:00:00'
      AND hora_fin = '11:00:00'
);

COMMIT;
