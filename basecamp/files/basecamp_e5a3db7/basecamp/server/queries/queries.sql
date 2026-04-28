-- name: CreateUser :exec
INSERT INTO users (username, password_hash)
VALUES (?, ?);

-- name: GetUserByUsername :one
SELECT id, username, password_hash, role
FROM users
WHERE username = ?;

-- name: ListCoursesWithCount :many
SELECT c.id, c.title, c.description, COUNT(l.id) AS lessons_count
FROM courses c
LEFT JOIN lessons l ON l.course_id = c.id
GROUP BY c.id, c.title, c.description, c.sort_order
ORDER BY c.sort_order;

-- name: GetCourse :one
SELECT id, title, description
FROM courses
WHERE id = ?;

-- name: ListLessonsByCourse :many
SELECT id, course_id, title, type
FROM lessons
WHERE course_id = ?
ORDER BY sort_order;

-- name: GetLesson :one
SELECT id, course_id, title, type
FROM lessons
WHERE id = ? AND course_id = ?;

-- name: GetLessonContent :one
SELECT id, course_id, title, type, content
FROM lessons
WHERE id = ? AND course_id = ?;
