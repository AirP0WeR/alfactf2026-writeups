package repository

import (
	"context"
	"database/sql"

	"server/internal/db"
	"server/internal/model"
)

type LessonRepo struct {
	q *db.Queries
}

func NewLessonRepo(database *sql.DB) *LessonRepo {
	return &LessonRepo{q: db.New(database)}
}

func (r *LessonRepo) Get(ctx context.Context, courseID, lessonID int) (*model.Lesson, error) {
	row, err := r.q.GetLesson(ctx, db.GetLessonParams{
		ID:       int64(lessonID),
		CourseID: int64(courseID),
	})
	if err != nil {
		return nil, err
	}
	return &model.Lesson{
		ID:       int(row.ID),
		CourseID: int(row.CourseID),
		Title:    row.Title,
		Type:     row.Type,
	}, nil
}

func (r *LessonRepo) GetContent(ctx context.Context, courseID, lessonID int) (*model.Lesson, error) {
	row, err := r.q.GetLessonContent(ctx, db.GetLessonContentParams{
		ID:       int64(lessonID),
		CourseID: int64(courseID),
	})
	if err != nil {
		return nil, err
	}
	return &model.Lesson{
		ID:       int(row.ID),
		CourseID: int(row.CourseID),
		Title:    row.Title,
		Type:     row.Type,
		Content:  row.Content,
	}, nil
}
