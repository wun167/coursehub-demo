-- THI NGHIEM race condition (cach lam KHONG an toan). Chi chay tren DB hoc tap.
-- Truoc khi bat dau: chay 08_week04_demo_setup.sql
-- Mo hai Query Tool: chay khoi TAB A, trong luc A dang pg_sleep thi chay ngay khoi TAB B.

-- ===================== TAB A =====================
BEGIN;
SELECT cs.id, cs.capacity, COUNT(e.student_id) AS enrolled
FROM class_sections AS cs
LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
WHERE cs.id = 'RACE-01'
GROUP BY cs.id, cs.capacity;

SELECT pg_sleep(8);

INSERT INTO enrollments (student_id, class_section_id)
VALUES ('22000002', 'RACE-01');
COMMIT;

-- ===================== TAB B =====================
BEGIN;
SELECT cs.id, cs.capacity, COUNT(e.student_id) AS enrolled
FROM class_sections AS cs
LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
WHERE cs.id = 'RACE-01'
GROUP BY cs.id, cs.capacity;

INSERT INTO enrollments (student_id, class_section_id)
VALUES ('22000004', 'RACE-01');
COMMIT;

-- ===================== KIEM TRA SAU KHI CA HAI TAB XONG =====================
SELECT cs.id, cs.capacity,
       COUNT(e.student_id) AS enrolled,
       cs.capacity - COUNT(e.student_id) AS remaining
FROM class_sections AS cs
LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
WHERE cs.id = 'RACE-01'
GROUP BY cs.id, cs.capacity;

SELECT student_id, class_section_id
FROM enrollments
WHERE class_section_id = 'RACE-01'
ORDER BY student_id;

-- Ket qua sai mong doi: enrolled = 2, remaining = -1.
-- RESET NGAY: chay lai 08_week04_demo_setup.sql
