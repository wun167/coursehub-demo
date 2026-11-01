-- THI NGHIEM row lock bang SELECT ... FOR UPDATE. Khong tao du lieu.
-- Mo hai Query Tool. Chay TAB A, ngay sau do chay TAB B: B se cho den khi A COMMIT.

-- ===================== TAB A =====================
BEGIN;
SELECT id, capacity FROM class_sections WHERE id = 'RACE-01' FOR UPDATE;
SELECT pg_sleep(8);
COMMIT;

-- ===================== TAB B =====================
BEGIN;
SELECT id, capacity FROM class_sections WHERE id = 'RACE-01' FOR UPDATE;
ROLLBACK;
