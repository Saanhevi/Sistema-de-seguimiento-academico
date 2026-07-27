-- HU22 · Agrega Usuario.documento a una base de datos que ya existe.
--
-- Database/schemas.sql solo se ejecuta la primera vez que se crea el volumen de
-- Postgres (ver README §2): sobre un volumen existente, `docker compose up` no
-- aplica ningún cambio de esquema. Este script cubre ese caso.
--
-- Cómo aplicarlo:
--   docker compose exec -T db psql -U postgres -d gestion_academica < Database/migraciones/001-usuario-documento.sql
--
-- Las dos sentencias son idempotentes (IF NOT EXISTS): correr la migración dos
-- veces no falla, que es justo lo que pasa cuando nadie recuerda si ya la corrió.
--
-- AVISO: quien haga `git pull` sin correr esto verá UndefinedColumn en cualquier
-- consulta que toque Usuario — o sea, en el login.

ALTER TABLE Usuario ADD COLUMN IF NOT EXISTS documento VARCHAR(20);
CREATE UNIQUE INDEX IF NOT EXISTS usuario_documento_key ON Usuario (documento);
