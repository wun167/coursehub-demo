-- Chay TUNG BUOC. Ghi scan type + Execution Time vao docs/week04_notes.md.

-- Buoc 1: EXPLAIN TRUOC index (chay rieng, chay 2-3 lan, lay lan on dinh)
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, class_section_id, event_type, occurred_at
FROM enrollment_events
WHERE dataset = 'performance'
  AND student_id = '22000001'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
ORDER BY occurred_at DESC
LIMIT 50;

-- Buoc 2: tao composite index (cot bang nhau truoc, cot thoi gian/sap xep sau)
CREATE INDEX idx_enrollment_events_dataset_student_time
ON enrollment_events (dataset, student_id, occurred_at DESC);

ANALYZE enrollment_events;

-- Buoc 3: EXPLAIN SAU index (cung cau truy van)
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, class_section_id, event_type, occurred_at
FROM enrollment_events
WHERE dataset = 'performance'
  AND student_id = '22000001'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
ORDER BY occurred_at DESC
LIMIT 50;

-- Kiem tra index da ton tai (neu bao "already exists")
-- SELECT indexname FROM pg_indexes WHERE tablename = 'enrollment_events';

-- Don bo du lieu performance (KHONG dung TRUNCATE)
-- DELETE FROM enrollment_events WHERE dataset = 'performance';
-- ANALYZE enrollment_events;
