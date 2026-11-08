// Ghép query string cho các API có tìm kiếm/phân trang phía server.
// Bỏ qua giá trị rỗng (null, undefined, "") để không gửi tham số thừa:
// ví dụ GET /courses không chấp nhận q rỗng (min_length=1).
export function buildQuery(params = {}) {
  const parts = Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== null && value !== "")
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
  return parts.length ? `?${parts.join("&")}` : "";
}
