package repository

import (
	"context"
	"database/sql"

	"server/internal/db"
	"server/internal/model"
)

type CourseRepo struct {
	q *db.Queries
}

func NewCourseRepo(database *sql.DB) *CourseRepo {
	return &CourseRepo{q: db.New(database)}
}

type CourseListItem struct {
	ID           int    `json:"id"`
	Title        string `json:"title"`
	Description  string `json:"description"`
	LessonsCount int    `json:"lessons_count"`
}

func (r *CourseRepo) ListWithCount(ctx context.Context) ([]CourseListItem, error) {
	rows, err := r.q.ListCoursesWithCount(ctx)
	if err != nil {
		return nil, err
	}
	items := make([]CourseListItem, len(rows))
	for i, row := range rows {
		items[i] = CourseListItem{
			ID:           int(row.ID),
			Title:        row.Title,
			Description:  row.Description,
			LessonsCount: int(row.LessonsCount),
		}
	}
	return items, nil
}

func (r *CourseRepo) GetWithLessons(ctx context.Context, courseID int) (*model.Course, error) {
	courseRow, err := r.q.GetCourse(ctx, int64(courseID))
	if err != nil {
		return nil, err
	}
	course := &model.Course{
		ID:          int(courseRow.ID),
		Title:       courseRow.Title,
		Description: courseRow.Description,
	}

	lessonRows, err := r.q.ListLessonsByCourse(ctx, int64(courseID))
	if err != nil {
		return nil, err
	}
	for _, l := range lessonRows {
		course.Lessons = append(course.Lessons, model.Lesson{
			ID:       int(l.ID),
			CourseID: int(l.CourseID),
			Title:    l.Title,
			Type:     l.Type,
		})
	}
	return course, nil
}
