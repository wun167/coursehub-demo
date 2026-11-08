// Kiểm thử api.js và query.js bằng fetch giả lập (không cần Backend/PostgreSQL).
// Chạy: npm test
import test from "node:test";
import assert from "node:assert/strict";
import { api } from "../src/api.js";
import { buildQuery } from "../src/query.js";

const realFetch = globalThis.fetch;
test.afterEach(() => { globalThis.fetch = realFetch; });

function mockFetch(status, body, { json = true } = {}) {
  const calls = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url, init });
    const text = body === undefined ? "" : json ? JSON.stringify(body) : body;
    return new Response(status === 204 ? null : text, { status });
  };
  return calls;
}

test("GET 200: trả về dữ liệu JSON và gọi đúng URL", async () => {
  const calls = mockFetch(200, [{ class_id: "WEB-01", remaining: 1 }]);
  const data = await api("/sections");
  assert.deepEqual(data, [{ class_id: "WEB-01", remaining: 1 }]);
  assert.equal(calls[0].url, "http://127.0.0.1:8000/sections");
  assert.equal(calls[0].init.method, "GET");
  assert.deepEqual(calls[0].init.headers, {});
  assert.equal(calls[0].init.body, undefined);
});

test("POST 201: gửi JSON đúng hai trường và header Content-Type", async () => {
  const calls = mockFetch(201, { message: "Dang ky thanh cong" });
  const body = { student_id: "22000004", class_section_id: "WEB-01" };
  const data = await api("/enrollments", { method: "POST", body });
  assert.equal(data.message, "Dang ky thanh cong");
  assert.equal(calls[0].init.method, "POST");
  assert.equal(calls[0].init.headers["Content-Type"], "application/json");
  assert.deepEqual(JSON.parse(calls[0].init.body), body);
});

test("DELETE 204: trả null, không đọc JSON", async () => {
  mockFetch(204);
  assert.equal(await api("/enrollments/22000004/WEB-01", { method: "DELETE" }), null);
});

test("404: lỗi mang status và nội dung detail", async () => {
  mockFetch(404, { detail: "Khong tim thay sinh vien" });
  await assert.rejects(api("/students/99999999/enrollments"), (err) => {
    assert.equal(err.status, 404);
    assert.match(err.message, /HTTP 404: Khong tim thay sinh vien/);
    return true;
  });
});

test("409: lớp hết chỗ được báo đúng", async () => {
  mockFetch(409, { detail: "Lop hoc phan da het cho" });
  await assert.rejects(
    api("/enrollments", { method: "POST", body: { student_id: "22000004", class_section_id: "RACE-01" } }),
    (err) => err.status === 409 && /het cho/.test(err.message),
  );
});

test("422: ghép detail dạng danh sách thành một chuỗi", async () => {
  mockFetch(422, { detail: [{ msg: "String should have at least 8 characters" }, { msg: "Field required" }] });
  await assert.rejects(api("/enrollments", { method: "POST", body: {} }), (err) => {
    assert.equal(err.status, 422);
    assert.match(err.message, /at least 8 characters; Field required/);
    return true;
  });
});

test("Mất kết nối: báo lỗi kết nối, không có status", async () => {
  globalThis.fetch = async () => { throw new TypeError("Failed to fetch"); };
  await assert.rejects(api("/sections"), (err) => {
    assert.match(err.message, /Không nhận được phản hồi API/);
    assert.equal(err.status, undefined);
    return true;
  });
});

test("AbortError: được ném lại nguyên vẹn để Effect bỏ qua", async () => {
  globalThis.fetch = async () => {
    const e = new Error("aborted"); e.name = "AbortError"; throw e;
  };
  await assert.rejects(api("/sections"), (err) => err.name === "AbortError");
});

test("Phản hồi không phải JSON: báo lỗi rõ ràng", async () => {
  mockFetch(200, "<html>oops</html>", { json: false });
  await assert.rejects(api("/sections"), /HTTP 200: phản hồi không phải JSON/);
});

test("Lỗi không có detail: dùng thông báo mặc định", async () => {
  mockFetch(500, {});
  await assert.rejects(api("/sections"), /HTTP 500: Yêu cầu không thành công/);
});

test("buildQuery: bỏ giá trị rỗng và mã hóa ký tự đặc biệt", () => {
  assert.equal(buildQuery({}), "");
  assert.equal(buildQuery({ q: "", skip: 0, limit: 6 }), "?skip=0&limit=6");
  assert.equal(buildQuery({ q: "cơ sở & dữ liệu", skip: 10 }),
    "?q=c%C6%A1%20s%E1%BB%9F%20%26%20d%E1%BB%AF%20li%E1%BB%87u&skip=10");
  assert.equal(buildQuery({ student_id: "22000004", event_type: undefined, skip: null }),
    "?student_id=22000004");
});
