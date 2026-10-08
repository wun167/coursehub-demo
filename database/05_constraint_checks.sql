-- Lỗi 1: Đăng ký trùng
INSERT INTO enrollments (student_id, class_section_id) VALUES ('22000001', 'WEB-01');

-- Lỗi 2: Sinh viên không tồn tại
INSERT INTO enrollments (student_id, class_section_id) VALUES ('22999999', 'WEB-01');

-- Lỗi 3: Sức chứa = 0
UPDATE class_sections SET capacity = 0 WHERE id = 'WEB-01';

-- Lỗi 4: Tín chỉ NULL
UPDATE courses SET credits = NULL WHERE code = 'INT2204';

-- Lỗi 5: Trùng email
UPDATE students SET email = 'anh@example.com' WHERE id = '22000002';

-- Lỗi 6: Tên chỉ gồm khoảng trắng
UPDATE students SET name = ' ' WHERE id = '22000004';