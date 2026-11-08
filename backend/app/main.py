from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from . import schemas
from .database import engine
from .schemas import EnrollmentCreate

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CourseHub API",
    version="0.4.0",
    description="API thuc hanh Buoi 4 - transaction, locking va hieu nang",
)

# Buoi 5: chi cho phep frontend local goi API qua trinh duyet.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "PATCH"],
    allow_headers=["Content-Type"],
)

# 1. Health Check
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "CourseHub API dang hoat dong"}

@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.exception("Khong ket noi duoc co so du lieu")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khong ket noi duoc co so du lieu",
        ) from exc
    return {"status": "ok", "database": "connected"}

# 2. Danh sách & tìm kiếm học phần
# Bài 4: mở rộng
@app.get("/courses", response_model=list[schemas.CourseOut])
def list_courses(
    q: str | None = Query(None, min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    sql = "SELECT code, name, credits FROM courses"
    params = {}
    
    if q:
        sql += " WHERE LOWER(name) LIKE LOWER(:q) OR LOWER(code) LIKE LOWER(:q)"
        params["q"] = f"%{q}%"
        
    sql += " ORDER BY code ASC LIMIT :limit OFFSET :skip"
    params["limit"] = limit
    params["skip"] = skip

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        return [dict(row._mapping) for row in result]

# 3. Chi tiết một học phần
@app.get("/courses/{course_code}")
def get_course(course_code: str) -> dict[str, object]:
    sql = "SELECT code, name, credits FROM courses WHERE code = :course_code"
    with engine.connect() as connection:
        row = connection.execute(text(sql), {"course_code": course_code.upper()}).mappings().first()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay hoc phan")
        return dict(row)

# 4. Danh sách lớp học phần (đọc View v_section_summary)
@app.get("/sections")
def list_sections(available_only: bool = False) -> list[dict[str, object]]:
    sql = "SELECT class_id, course_code, capacity, enrolled, remaining FROM v_section_summary"
    if available_only:
        sql += " WHERE remaining > 0"
    sql += " ORDER BY class_id"
    with engine.connect() as connection:
        rows = connection.execute(text(sql)).mappings().all()
        return [dict(row) for row in rows]

# Bài 2: Chi tiết học phần
@app.get("/sections/{section_id}", response_model=schemas.SectionDetailOut)
def get_section_detail(section_id: str):
    sql = """
        SELECT 
            cs.id AS section_id,
            cs.course_code,
            c.name AS course_title,
            cs.semester_code AS semester,
            l.name AS lecturer_name,
            cs.capacity,
            COALESCE(v.enrolled, 0) AS enrolled,
            COALESCE(v.remaining, cs.capacity) AS remaining
        FROM class_sections cs
        LEFT JOIN courses c ON cs.course_code = c.code
        LEFT JOIN lecturers l ON cs.lecturer_id = l.id
        LEFT JOIN v_section_summary v ON cs.id = v.class_id
        WHERE cs.id = :section_id
    """
    with engine.connect() as conn:
        row = conn.execute(text(sql), {"section_id": section_id}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Lop hoc phan khong ton tai")
        return dict(row)

# 5. Các lớp một sinh viên đã đăng ký
@app.get("/students/{student_id}/enrollments")
def list_student_enrollments(student_id: str) -> list[dict[str, object]]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    enrollment_sql = """
        SELECT e.student_id, s.name AS student_name, cs.id AS class_section_id,
               c.code AS course_code, c.name AS course_name, e.registered_at
        FROM enrollments AS e
        JOIN students AS s ON s.id = e.student_id
        JOIN class_sections AS cs ON cs.id = e.class_section_id
        JOIN courses AS c ON c.code = cs.course_code
        WHERE e.student_id = :student_id
        ORDER BY cs.id
    """
    with engine.connect() as connection:
        student = connection.execute(text(student_sql), {"student_id": student_id}).first()
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay sinh vien")
        rows = connection.execute(text(enrollment_sql), {"student_id": student_id}).mappings().all()
        return [dict(row) for row in rows]

# Bài 1: danh sách giảng viên
@app.get("/lecturers", response_model=list[schemas.LecturerOut])
def list_lecturers():
    sql = "SELECT id, name FROM lecturers ORDER BY id ASC"
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return [dict(row._mapping) for row in result]

# 6. Đăng ký học phần mới (POST) - khóa dòng lớp để tránh race condition
@app.post("/enrollments", status_code=status.HTTP_201_CREATED)
def create_enrollment(payload: EnrollmentCreate) -> dict[str, str]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    lock_section_sql = """
        SELECT id, capacity
        FROM class_sections
        WHERE id = :class_section_id
        FOR UPDATE
    """
    duplicate_sql = """
        SELECT 1
        FROM enrollments
        WHERE student_id = :student_id
          AND class_section_id = :class_section_id
    """
    count_sql = """
        SELECT COUNT(*)
        FROM enrollments
        WHERE class_section_id = :class_section_id
    """
    insert_sql = """
        INSERT INTO enrollments (student_id, class_section_id)
        VALUES (:student_id, :class_section_id)
    """
    event_sql = """
        INSERT INTO enrollment_events
            (student_id, class_section_id, event_type, source, dataset)
        VALUES
            (:student_id, :class_section_id, 'CREATED', 'api', 'demo')
    """
    parameters = {
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }

    try:
        with engine.begin() as connection:
            student = connection.execute(
                text(student_sql),
                {"student_id": payload.student_id},
            ).first()
            if student is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay sinh vien",
                )

            # Khóa dòng lớp học phần: mọi đăng ký cùng lớp xếp hàng tại đây
            section = connection.execute(
                text(lock_section_sql),
                {"class_section_id": payload.class_section_id},
            ).mappings().first()
            if section is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay lop hoc phan",
                )

            duplicated = connection.execute(
                text(duplicate_sql), parameters
            ).first()
            if duplicated is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sinh vien da dang ky lop nay",
                )

            enrolled = connection.execute(
                text(count_sql),
                {"class_section_id": payload.class_section_id},
            ).scalar_one()
            if int(enrolled) >= int(section["capacity"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Lop hoc phan da het cho",
                )

            connection.execute(text(insert_sql), parameters)
            connection.execute(text(event_sql), parameters)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dang ky xung dot voi du lieu hien tai",
        ) from exc

    return {
        "message": "Dang ky thanh cong",
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }


# 7. Hủy đăng ký học phần (DELETE) - cùng thứ tự khóa với POST, ghi sự kiện CANCELLED
@app.delete(
    "/enrollments/{student_id}/{class_section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_enrollment(student_id: str, class_section_id: str) -> Response:
    lock_section_sql = """
        SELECT id
        FROM class_sections
        WHERE id = :class_section_id
        FOR UPDATE
    """
    delete_sql = """
        DELETE FROM enrollments
        WHERE student_id = :student_id
          AND class_section_id = :class_section_id
        RETURNING student_id
    """
    event_sql = """
        INSERT INTO enrollment_events
            (student_id, class_section_id, event_type, source, dataset)
        VALUES
            (:student_id, :class_section_id, 'CANCELLED', 'api', 'demo')
    """
    parameters = {
        "student_id": student_id,
        "class_section_id": class_section_id,
    }

    with engine.begin() as connection:
        section = connection.execute(
            text(lock_section_sql),
            {"class_section_id": class_section_id},
        ).first()
        if section is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay lop hoc phan",
            )

        deleted = connection.execute(
            text(delete_sql), parameters
        ).first()
        if deleted is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay dang ky can huy",
            )

        connection.execute(text(event_sql), parameters)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Bài 1 (Buổi 4): lịch sử đăng ký
@app.get("/enrollment-events")
def list_enrollment_events(
    student_id: str | None = None,
    event_type: str | None = Query(None, pattern="^(CREATED|CANCELLED)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[dict[str, object]]:
    sql = """
        SELECT id, student_id, class_section_id, event_type,
               source, dataset, occurred_at
        FROM enrollment_events
        WHERE dataset = 'demo'
          AND (CAST(:student_id AS VARCHAR) IS NULL OR student_id = :student_id)
          AND (CAST(:event_type AS VARCHAR) IS NULL OR event_type = :event_type)
        ORDER BY occurred_at DESC, id DESC
        LIMIT :limit OFFSET :skip
    """
    with engine.connect() as connection:
        rows = connection.execute(
            text(sql),
            {
                "student_id": student_id,
                "event_type": event_type,
                "skip": skip,
                "limit": limit,
            },
        ).mappings().all()
    return [
        {**dict(row), "occurred_at": row["occurred_at"].isoformat()}
        for row in rows
    ]


# Bài 3: Cập nhật sức chứa
@app.patch("/sections/{section_id}/capacity")
def update_section_capacity(section_id: str, payload: schemas.CapacityUpdateIn):
    with engine.connect() as conn:
        # 1. Kiểm tra lớp học phần tồn tại và lấy số lượng đã đăng ký hiện tại
        check_sql = """
            SELECT cs.capacity, COALESCE(v.enrolled, 0) AS enrolled
            FROM class_sections cs
            LEFT JOIN v_section_summary v ON cs.id = v.class_id
            WHERE cs.id = :section_id
        """
        row = conn.execute(text(check_sql), {"section_id": section_id}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Lop hoc phan khong ton tai")

        # 2. Ràng buộc: Sức chứa mới không được nhỏ hơn số sinh viên đã đăng ký
        if payload.capacity < row["enrolled"]:
            raise HTTPException(
                status_code=409, 
                detail=f"Suc chua moi ({payload.capacity}) khong the nho hon so luong da dang ky ({row['enrolled']})"
            )

        # 3. Cập nhật sức chứa
        update_sql = "UPDATE class_sections SET capacity = :capacity WHERE id = :section_id"
        conn.execute(text(update_sql), {"capacity": payload.capacity, "section_id": section_id})
        conn.commit()

        return {
            "message": "Cap nhat suc chua thanh cong",
            "section_id": section_id,
            "new_capacity": payload.capacity
        }
