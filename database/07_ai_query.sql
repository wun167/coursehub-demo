-- Đếm sai (Dùng COUNT(*))
SELECT cs.id, COUNT(*) AS enrolled
FROM class_sections AS cs
LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
WHERE cs.id = 'WEB-02'
GROUP BY cs.id;

-- Đếm đúng (Dùng COUNT(e.student_id))
SELECT cs.id, COUNT(e.student_id) AS enrolled
FROM class_sections AS cs
LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
WHERE cs.id = 'WEB-02'
GROUP BY cs.id;