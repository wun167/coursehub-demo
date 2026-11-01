from pydantic import BaseModel, Field
from pydantic import Field

class EnrollmentCreate(BaseModel):
    student_id: str = Field(min_length=8, max_length=8, examples=["22000004"])
    class_section_id: str = Field(min_length=1, max_length=20, examples=["WEB-01"])

class CourseOut(BaseModel):
    code: str
    name: str
    credits: int

# Bài tập thực hành

# Bài 1:
class LecturerOut(BaseModel):
    id: str
    name: str

# Bài 2:
from pydantic import BaseModel

class SectionDetailOut(BaseModel):
    section_id: str
    course_code: str
    course_title: str
    semester: str
    lecturer_name: str | None = None
    capacity: int
    enrolled: int
    remaining: int

    class Config:
        from_attributes = True

# Bài 3:
class CapacityUpdateIn(BaseModel):
    capacity: int = Field(..., gt=0, description="Suc chua phai lon hon 0")