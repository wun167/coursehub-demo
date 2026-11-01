# CourseHub - Buoi 4

- Migration 001: enrollment_events (+ schema_migrations).
- Migration 002 (Bai 4): them cot note VARCHAR(200) vao enrollment_events.
- Demo class: RACE-01, capacity = 1.
- Race condition (file 09): hai transaction cung doc "con cho" roi cung INSERT => RACE-01 co 2 dang ky du capacity = 1.
- Row lock (file 10): Tab B cho khoang 8 giay den khi Tab A COMMIT.
- POST /enrollments: lock class_sections bang FOR UPDATE.
- Concurrency test: 1 request 201, 1 request 409.
  - Lan 1: 22000002 -> 201, 22000004 -> 409; RACE-01 enrolled = 1, remaining = 0.
  - Lan 2: 22000002 -> 409, 22000004 -> 201; RACE-01 enrolled = 1, remaining = 0.
- Performance data: 100000 rows, dataset=performance.
- Index: idx_enrollment_events_dataset_student_time (dataset, student_id, occurred_at DESC).

## Ket qua EXPLAIN (do tren may cua toi)

Truy van: 50 su kien gan nhat cua sinh vien 22000001 (dataset = 'performance', occurred_at >= 2025-12-20), ORDER BY occurred_at DESC LIMIT 50.

| | Truoc index | Sau index |
|---|---|---|
| Scan type | Seq Scan + Sort (top-N heapsort) | Index Scan using idx_enrollment_events_dataset_student_time |
| Rows Removed by Filter | 99180 | Khong co (dieu kien nam trong Index Cond) |
| Buffers (shared hit/read) | hit=1137, read=0 | hit=50, read=3 |
| Planning Time (ms) | 0.373 | 0.576 |
| Execution Time (ms) | 8.936 | 1.093 |

Nhan xet:
- Truoc index, PostgreSQL doc toan bo bang (loai 99180 dong), sau do sap xep de lay 50 dong.
- Sau index, chi doc dung vung (dataset, student_id) va duyet theo thu tu occurred_at DESC nen dung ngay khi du 50 dong; khong can Sort.
- Execution Time giam khoang 8.2 lan (8.936 ms -> 1.093 ms); so block doc giam tu 1137 xuong 53. Planning Time tang nhe (0.373 -> 0.576 ms), khong dang ke.
- So lieu phu thuoc may va cache; khong dung de ket luan ty le tang toc co dinh.

## Project nhom - Checkpoint 1 (SmartTrip)

| Noi dung | Cau tra loi | Nguoi thuc hien | Nguoi kiem tra |
|---|---|---|---|
| Transaction nhieu bang | Dat phong: INSERT bookings + INSERT booking_events (CREATED) + kiem tra suc chua phong trong cung mot transaction; loi o buoc nao thi ROLLBACK ca ba | Khoi | Loc |
| Nguy co dong thoi | Hai khach cung dat phong cuoi cung (con 1 cho) trong cung khoang ngay; neu khong khoa, ca hai cung doc "con cho" roi cung INSERT => phong bi dat vuot suc chua | Dung | Tester |
| Dong/tai nguyen can khoa | Dong phong trong bang rooms: SELECT ... FOR UPDATE truoc khi dem booking trung ngay, roi moi INSERT (cung thu tu khoa o API huy dat phong) | Khoi | Loc |
| Migration dau tien | Alembic 0001_init_schema: users, rooms, bookings, booking_events (khoa ngoai, CHECK status/event_type); 0002 them index sau khi do | Lam | Dung |
| Truy van can do | Lich su dat phong cua mot nguoi dung theo thoi gian: WHERE user_id = ? AND created_at >= ? ORDER BY created_at DESC LIMIT 50, tren du lieu lon (khoang 100.000 dong) | Loc | Khoi |
| Chi muc du kien | (user_id, created_at DESC) tren booking_events: cot so sanh bang dat truoc, cot thoi gian/sap xep dat sau; do EXPLAIN (ANALYZE, BUFFERS) truoc/sau | Lam | Dung |
| Cach kiem thu | pytest + ThreadPoolExecutor + Barrier (marker concurrency), file backend/tests/concurrency/test_book_last_room.py: phong con 1 cho, 2 khach dat cung luc, assert dung mot 201 va mot 409; sau do truy van xac nhan so booking cua phong = 1 | Tester | Khoi |

Khong commit backend/.env.
