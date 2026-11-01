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

## Bai 1 - API doc lich su dang ky
- Endpoint: GET /enrollment-events (query: student_id, event_type, skip, limit; limit 1-100; sap xep occurred_at DESC, id DESC; dung bind parameter).
- Postman (CourseHub_Buoi_4.postman_collection.json):
  - 11 - co du lieu: ?student_id=22000004&limit=10 -> 200, tra ve mang.
  - 12 - khong co du lieu: ?student_id=99999999 -> 200, mang rong.

## Bai 2 - Test rollback nhieu bang
- Script: backend/tests/week04_rollback_test.py (chay: python -m backend.tests.week04_rollback_test).
- Trong mot transaction: INSERT enrollments thanh cong, sau do INSERT enrollment_events voi event_type = 'INVALID' vi pham CHECK ck_enrollment_events_type.
- Ket qua: transaction bi ROLLBACK ca hai bang; enrollments truoc = 1, sau = 1 (khong tang); in PASS.
- (So 1 la dang ky con lai trong RACE-01 tu lan test truoc, khong anh huong ket qua vi chi so sanh truoc/sau.)

## Bai 3 - Chi muc thu hai
Truy van: dem su kien CREATED cua WEB-01 trong thang 6/2025 (dataset = 'performance'). Ket qua ca hai lan deu 1644 dong.

| | Truoc index | Sau index |
|---|---|---|
| Scan type | Bitmap Heap Scan (Bitmap Index Scan tren idx_enrollment_events_dataset_student_time) | Index Only Scan using idx_enrollment_events_section_type_time |
| Rows Removed by Filter | 6576 | Khong co (ca 5 dieu kien nam trong Index Cond) |
| Heap Fetches | - | 0 |
| Buffers | hit=382, read=66 | hit=16 |
| Planning Time (ms) | 0.443 | 0.170 |
| Execution Time (ms) | 11.557 | 0.362 |

Index: idx_enrollment_events_section_type_time (dataset, class_section_id, event_type, occurred_at).

Ly do thu tu cot: dataset, class_section_id, event_type la dieu kien so sanh bang nen dat truoc; occurred_at la dieu kien khoang nen dat cuoi de PostgreSQL tim dung vung roi doc lien tiep.

Nhan xet:
- Truoc index, PostgreSQL dung index cu (dataset, student_id, occurred_at). Index cu chi giup loc dataset va occurred_at, khong co class_section_id va event_type, nen doc ve 8220 dong roi loc bo 6576 dong.
- Sau index, ca 5 dieu kien nam trong Index Cond, PostgreSQL chi doc dung 1644 dong can dem. Truy van chi dem nen cac cot deu co trong index, dan den Index Only Scan, Heap Fetches = 0, khong can doc bang.
- Execution Time giam khoang 32 lan (11.557 ms -> 0.362 ms); so block doc giam tu 448 xuong 16.
- Luu y: so "truoc" co read=66 (lan do dau, du lieu chua nam het trong cache) nen muc tang toc co phan do cache. So lieu phu thuoc may, khong dung de ket luan ty le co dinh.
- Doi gia: index them dung luong va lam cham INSERT, nen khong tao index cho moi cot.

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