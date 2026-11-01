from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.app.database import engine

SQL_COUNT = """
    SELECT COUNT(*) FROM enrollments WHERE class_section_id = 'RACE-01'
"""


def count_enrollments() -> int:
    with engine.connect() as conn:
        return int(conn.execute(text(SQL_COUNT)).scalar_one())


def main() -> None:
    before = count_enrollments()
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO enrollments (student_id, class_section_id) "
                "VALUES ('22000004', 'RACE-01')"
            ))
            # event_type khong hop le -> vi pham CHECK -> ROLLBACK ca transaction
            conn.execute(text(
                "INSERT INTO enrollment_events "
                "(student_id, class_section_id, event_type) "
                "VALUES ('22000004', 'RACE-01', 'INVALID')"
            ))
    except IntegrityError as exc:
        print("Loi du kien:", str(exc.orig).splitlines()[0])

    after = count_enrollments()
    print(f"enrollments truoc = {before}, sau = {after}")
    assert before == after, "Rollback that bai: enrollments da tang"
    print("PASS: INSERT enrollments da bi rollback cung enrollment_events.")


if __name__ == "__main__":
    main()