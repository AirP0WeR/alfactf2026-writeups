package repository

import (
	"context"
	"database/sql"
	"errors"

	"server/internal/db"
	"server/internal/model"
)

type UserRepo struct {
	q *db.Queries
}

func NewUserRepo(database *sql.DB) *UserRepo {
	return &UserRepo{q: db.New(database)}
}

func (r *UserRepo) Create(ctx context.Context, username, passwordHash string) error {
	return r.q.CreateUser(ctx, db.CreateUserParams{
		Username:     username,
		PasswordHash: passwordHash,
	})
}

func (r *UserRepo) GetByUsername(ctx context.Context, username string) (*model.User, error) {
	row, err := r.q.GetUserByUsername(ctx, username)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	return &model.User{
		ID:           int(row.ID),
		Username:     row.Username,
		PasswordHash: row.PasswordHash,
		Role:         row.Role,
	}, nil
}
