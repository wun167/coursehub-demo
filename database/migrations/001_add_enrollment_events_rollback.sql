-- Rollback migration 001: CHI DUNG KHI CHAP NHAN MAT TOAN BO LICH SU SU KIEN
BEGIN;
DROP TABLE enrollment_events;
DELETE FROM schema_migrations WHERE version = '001';
COMMIT;
