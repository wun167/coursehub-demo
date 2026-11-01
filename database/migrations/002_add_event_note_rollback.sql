-- Rollback migration 002: XOA COT note => MAT du lieu ghi chu da nhap (cac cot khac khong doi)
BEGIN;
ALTER TABLE enrollment_events DROP COLUMN note;
DELETE FROM schema_migrations WHERE version = '002';
COMMIT;
