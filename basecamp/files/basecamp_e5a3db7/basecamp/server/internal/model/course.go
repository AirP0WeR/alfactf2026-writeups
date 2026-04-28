package model

type Course struct {
	ID          int      `json:"id"`
	Title       string   `json:"title"`
	Description string   `json:"description"`
	Lessons     []Lesson `json:"lessons,omitempty"`
}
