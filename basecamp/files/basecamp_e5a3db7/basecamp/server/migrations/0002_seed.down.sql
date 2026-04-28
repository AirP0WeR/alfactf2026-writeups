DELETE FROM lessons;
DELETE FROM courses;
DELETE FROM sqlite_sequence WHERE name IN ('lessons', 'courses', 'users');
