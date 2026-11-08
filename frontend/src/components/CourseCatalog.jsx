import { useEffect, useState } from "react";
import { api } from "../api.js";
import { buildQuery } from "../query.js";
import Notice from "./Notice.jsx";

// Bài 4: tìm kiếm + phân trang PHÍA SERVER cho danh sách học phần.
//   API:        GET /courses?q=<từ khóa>&skip=<offset>&limit=<kích thước trang>
//   q:          tùy chọn, tối thiểu 1 ký tự (không gửi khi ô tìm kiếm rỗng)
//   skip:       >= 0, bằng (số trang - 1) * limit
//   limit:      1..100 (Backend từ chối giá trị ngoài khoảng); giao diện chỉ cho 2/5/10/20
//   sắp xếp:    ORDER BY code ASC - code là khóa chính nên thứ tự ổn định, không lặp/mất dòng giữa các trang
// Lọc/cắt mảng trong trình duyệt KHÔNG phải là phân trang CSDL, nên không dùng ở đây.
const PAGE_SIZES = [2, 5, 10, 20];
const MAX_PAGE_SIZE = 100;
const DEBOUNCE_MS = 300;

export default function CourseCatalog() {
  const [draft, setDraft] = useState("");
  const [q, setQ] = useState("");
  const [size, setSize] = useState(5);
  const [page, setPage] = useState(0);
  const [items, setItems] = useState([]);
  const [hasNext, setHasNext] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Chờ người dùng ngừng gõ rồi mới gọi API, tránh một request cho mỗi phím.
  useEffect(() => {
    const timer = setTimeout(() => {
      setQ(draft.trim());
      setPage(0);
    }, DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [draft]);

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      setLoading(true);
      setError("");
      try {
        const limit = Math.min(size, MAX_PAGE_SIZE);
        const query = buildQuery({ q, skip: page * limit, limit: limit + 1 });
        const data = await api(`/courses${query}`, { signal: controller.signal });
        if (controller.signal.aborted) return;
        setHasNext(data.length > limit);
        setItems(data.slice(0, limit));
      } catch (err) {
        if (controller.signal.aborted) return;
        setError(err.message);
        setItems([]);
        setHasNext(false);
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    load();
    return () => controller.abort();
  }, [q, size, page]);

  function changeSize(value) {
    setSize(Number(value));
    setPage(0);
  }

  const first = items.length === 0 ? 0 : page * size + 1;
  const last = page * size + items.length;

  return (
    <section className="panel" aria-labelledby="catalog-title">
      <h2 id="catalog-title">5. Danh mục học phần (tìm kiếm và phân trang phía server)</h2>
      <div className="filters">
        <label htmlFor="course-search">Tìm theo mã hoặc tên học phần</label>
        <input id="course-search" value={draft} placeholder="Ví dụ: INT2204 hoặc python"
          onChange={(e) => setDraft(e.target.value)} />
        <label htmlFor="page-size" className="inline-label">Số dòng / trang</label>
        <select id="page-size" value={size} onChange={(e) => changeSize(e.target.value)}>
          {PAGE_SIZES.map((n) => <option key={n} value={n}>{n}</option>)}
        </select>
      </div>
      <Notice kind="error">{error}</Notice>
      {loading && !error && <Notice>Đang tải học phần...</Notice>}
      {!loading && !error && items.length === 0 && (
        <p className="empty">Không có học phần phù hợp.</p>
      )}
      {!error && items.length > 0 && (
        <div className="table-scroll">
          <table aria-label="Danh mục học phần">
            <thead>
              <tr><th>Mã học phần</th><th>Tên học phần</th><th>Tín chỉ</th></tr>
            </thead>
            <tbody>
              {items.map((course) => (
                <tr key={course.code}>
                  <td><strong>{course.code}</strong></td>
                  <td>{course.name}</td>
                  <td>{course.credits}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="pager">
        <button type="button" className="secondary"
          disabled={loading || page === 0}
          onClick={() => setPage((p) => p - 1)}>Trang trước</button>
        <span className="muted">
          Trang {page + 1}{items.length > 0 ? ` · dòng ${first}-${last}` : ""}
        </span>
        <button type="button" className="secondary"
          disabled={loading || !hasNext}
          onClick={() => setPage((p) => p + 1)}>Trang sau</button>
      </div>
    </section>
  );
}
