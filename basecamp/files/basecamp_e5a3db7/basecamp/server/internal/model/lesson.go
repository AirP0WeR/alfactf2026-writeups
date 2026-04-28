package model

type Lesson struct {
	ID       int    `json:"id"`
	CourseID int    `json:"course_id"`
	Title    string `json:"title"`
	Type     string `json:"type"`
	Content  string `json:"content,omitempty"`
}
