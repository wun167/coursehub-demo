# CourseHub - Buoi 5: React frontend + FastAPI

## Da lam
- Them `frontend/` (React 18.2.0 + Vite 7.1.7) goi API that cua Buoi 3-4; khong tao lai database/project.
- Backend: chi them CORS trong `backend/app/main.py` (origin 5173; methods GET, POST, DELETE, PATCH). Giu nguyen nghiep vu, row lock `FOR UPDATE`, version 0.4.0.
- Component: `App`, `StudentForm`, `SectionTable`, `EnrollmentList`, `Notice`, `EnrollmentHistory`, `CourseCatalog`; `api.js` xu ly 204, loi 422/404/409, mat ket noi, AbortError.

## Cach chay
```
# Terminal 1 (thu muc goc)
.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload
# Terminal 2
cd frontend
copy .env.example .env.local
npm install
npm run dev        # http://127.0.0.1:5173/
npm test           # 11 test api.js / query.js
npm run build
```

## Luong Frontend - API - CSDL
| Thao tac | API | Ket qua quan sat |
|---|---|---|
| Tai lop / hoc phan | GET /courses?limit=100; GET /sections | Bang lop, so cho tu v_section_summary |
| Xem dang ky | GET /students/{id}/enrollments | 200; sinh vien chua dang ky -> mang rong; 99999999 -> 404 |
| Dang ky | POST /enrollments {student_id, class_section_id} | 201; WEB-01 3/2/1 -> 3/3/0; CSDL co dong enrollments + event CREATED |
| Huy dang ky | DELETE /enrollments/{student_id}/{class_section_id} | 204 khong body; WEB-01 ve 3/2/1; them event CANCELLED, CREATED cu van con |
| Lop het cho (cua so cu) | POST /enrollments | 409 "Lop hoc phan da het cho"; giao dien tai lai va hien "Het cho" |

Anh minh hoa: `docs/img/week05_*.png` (giao dien ban dau, sau dang ky WEB-01, 409 RACE-01, mobile 390px, Backend dung).

## Bai tap
- **Bai 1**: `components/StudentForm.jsx`. State `draftId/studentId` van o `App`, truyen xuong bang props (`draftId, studentId, busy, loading, onDraftChange, onSubmit, onReload`) nen khong co ban sao state.
- **Bai 2**: o chon hoc phan (INT2204/INT2205/INT2206) lay tu GET /courses?limit=100 (mac dinh limit cua /courses chi la 10). Loc trong `rows`; khong co lop phu hop -> "Khong co lop phu hop voi bo loc.", khong sua CSDL.
- **Bai 3**: `components/EnrollmentHistory.jsx` dung GET /enrollment-events (Buoi 4). Backend chi tra dataset = 'demo'; moi trang 10 dong, xin 11 dong de biet con trang sau (`skip`, `limit=11`); loc event_type CREATED/CANCELLED; tu tai lai sau moi POST/DELETE.
- **Bai 4**: `components/CourseCatalog.jsx` tim kiem + phan trang phia server tren GET /courses.
  - Tham so: `q` (tuy chon, >= 1 ky tu, khong gui khi rong), `skip` >= 0, `limit` 1-100 (giao dien chi cho 2/5/10/20; hang so `MAX_PAGE_SIZE = 100`).
  - Sap xep: `ORDER BY code ASC`; `code` la khoa chinh nen thu tu on dinh, khong lap/mat dong giua cac trang.
  - Debounce 300 ms; AbortController huy request cu.
  - Ap dung cho project nhom: cung mau cho danh sach phong/booking cua SmartTrip (sap xep theo cot duy nhat, vi du `created_at DESC, id DESC`).

## Kiem thu da chay
- `npm test`: 11/11 pass (GET, POST, DELETE 204, 404, 409, 422, mat ket noi, AbortError, khong phai JSON, loi khong co detail, buildQuery).
- `npm run build`: thanh cong.
- Kiem thu trinh duyet tu dong tren PostgreSQL 16 voi schema/seed/migration 001-002 cua repo: 44/44 buoc pass (dang ky/huy co doi chieu SQL, 404, ma ngan, hai cua so RACE-01 -> 409, phan trang lich su, phan trang/tim kiem hoc phan, debounce, mobile 390px khong tran ngang).
- Chua thay the: test concurrency hai worker cua Buoi 4 (`backend/tests/week04_concurrency_test.py`) - van chay rieng khi can.
- Cac buoc lam tren may ban (Figma, anh chup thuc te, git/PR) can tu hoan tat va ghi ket qua that.
