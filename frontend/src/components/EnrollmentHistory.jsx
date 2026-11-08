import { useEffect, useState } from "react";
import { api } from "../api.js";
import { buildQuery } from "../query.js";
import Notice from "./Notice.jsx";

// Bài 3: lịch sử đăng ký của sinh viên, có phân trang phía server.
// GET /enrollment-events đã lọc dataset = 'demo' và giới hạn limit <= 100,
// nên trình duyệt không bao giờ tải 100.000 sự kiện performance.
const PAGE_SIZE = 10;
const TYPE_LABEL = { CREATED: "Đăng ký", CANCELLED: "Hủy đăng ký" };

export default function EnrollmentHistory({ studentId, refresh }) {
  const [eventType, setEventType] = useState("");
  const [page, setPage] = useState(0);
  const [items, setItems] = useState([]);
  const [hasNext, setHasNext] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      setLoading(true);
      setError("");
      try {
        // Xin PAGE_SIZE + 1 dòng: nếu nhận đủ dòng thứ PAGE_SIZE + 1 thì còn trang sau.
        const query = buildQuery({
          student_id: studentId,
          event_type: eventType,
          skip: page * PAGE_SIZE,
          limit: PAGE_SIZE + 1,
        });
        const data = await api(`/enrollment-events${query}`, { signal: controller.signal });
        if (controller.signal.aborted) return;
        setHasNext(data.length > PAGE_SIZE);
        setItems(data.slice(0, PAGE_SIZE));
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
  }, [studentId, eventType, page, refresh]);

  function changeType(value) {
    setEventType(value);
    setPage(0);
  }

  return (
    <section className="panel" aria-labelledby="history-title">
      <h2 id="history-title">4. Lịch sử đăng ký (dữ liệu demo)</h2>
      <div className="history-controls">
        <label htmlFor="event-type" className="inline-label">Loại sự kiện</label>
        <select id="event-type" value={eventType}
          onChange={(e) => changeType(e.target.value)}>
          <option value="">Tất cả</option>
          <option value="CREATED">Đăng ký (CREATED)</option>
          <option value="CANCELLED">Hủy đăng ký (CANCELLED)</option>
        </select>
        <span className="muted">Sinh viên {studentId}</span>
      </div>
      <Notice kind="error">{error}</Notice>
      {loading && !error && <Notice>Đang tải lịch sử...</Notice>}
      {!loading && !error && items.length === 0 && (
        <p className="empty">Chưa có sự kiện nào cho bộ lọc này.</p>
      )}
      {!error && items.length > 0 && (
        <div className="table-scroll">
          <table aria-label="Lịch sử đăng ký">
            <thead>
              <tr><th>Thời điểm</th><th>Lớp</th><th>Sự kiện</th><th>Nguồn</th></tr>
            </thead>
            <tbody>
              {items.map((event) => (
                <tr key={event.id}>
                  <td>{event.occurred_at.slice(0, 19).replace("T", " ")}</td>
                  <td><strong>{event.class_section_id}</strong></td>
                  <td>
                    <span className={`tag ${event.event_type.toLowerCase()}`}>
                      {TYPE_LABEL[event.event_type] ?? event.event_type}
                    </span>
                  </td>
                  <td>{event.source}</td>
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
        <span className="muted">Trang {page + 1}</span>
        <button type="button" className="secondary"
          disabled={loading || !hasNext}
          onClick={() => setPage((p) => p + 1)}>Trang sau</button>
      </div>
    </section>
  );
}
