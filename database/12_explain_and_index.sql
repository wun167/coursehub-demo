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
CREATE INDEX IF NOT EXISTS idx_enrollment_events_dataset_student_time
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

-- Bài 3 --
-- Buoc 1: EXPLAIN truoc index (chay 2-3 lan, lay lan on dinh)
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM enrollment_events
WHERE dataset = 'performance'
  AND class_section_id = 'WEB-01'
  AND event_type = 'CREATED'
  AND occurred_at >= TIMESTAMP '2025-06-01 00:00:00'
  AND occurred_at <  TIMESTAMP '2025-07-01 00:00:00';

-- Buoc 2: tao index (cot so sanh bang truoc, cot khoang thoi gian sau)
CREATE INDEX IF NOT EXISTS idx_enrollment_events_section_type_time
ON enrollment_events (dataset, class_section_id, event_type, occurred_at);

ANALYZE enrollment_events;

-- Buoc 3: EXPLAIN sau index (cung cau truy van o Buoc 1)
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM enrollment_events
WHERE dataset = 'performance'
  AND class_section_id = 'WEB-01'
  AND event_type = 'CREATED'
  AND occurred_at >= TIMESTAMP '2025-06-01 00:00:00'
  AND occurred_at <  TIMESTAMP '2025-07-01 00:00:00';