-- Migration 002 (Bai 4): them cot note cho enrollment_events
-- Du lieu cu giu nguyen; cot moi cho phep NULL.
BEGIN;

ALTER TABLE enrollment_events
    ADD COLUMN note VARCHAR(200);

INSERT INTO schema_migrations (version, description)
VALUES ('002', 'Add note column to enrollment_events');

COMMIT;
