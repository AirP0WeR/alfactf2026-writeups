package handler

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"server/internal/middleware"
	"server/internal/repository"
	"server/internal/slug"
)

type CourseHandler struct {
	courseRepo *repository.CourseRepo
	slugSecret string
	logger     *zap.Logger
}

func NewCourseHandler(courseRepo *repository.CourseRepo, slugSecret string, logger *zap.Logger) *CourseHandler {
	return &CourseHandler{
		courseRepo: courseRepo,
		slugSecret: slugSecret,
		logger:     logger,
	}
}

func (h *CourseHandler) ListCourses(c *gin.Context) {
	courses, err := h.courseRepo.ListWithCount(c.Request.Context())
	if err != nil {
		h.logger.Error("ошибка получения курсов", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Внутренняя ошибка сервера"})
		return
	}
	if courses == nil {
		courses = []repository.CourseListItem{}
	}
	c.JSON(http.StatusOK, gin.H{"courses": courses})
}

type lessonListItem struct {
	ID    int    `json:"id"`
	Title string `json:"title"`
	Type  string `json:"type"`
	Slug  string `json:"slug,omitempty"`
}

func (h *CourseHandler) GetCourse(c *gin.Context) {
	courseID, err := strconv.Atoi(c.Param("course_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректный ID курса"})
		return
	}

	course, err := h.courseRepo.GetWithLessons(c.Request.Context(), courseID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Курс не найден"})
		return
	}

	claims, _ := middleware.GetClaims(c)
	isVIP := claims != nil && claims.Role == "vip"

	lessons := make([]lessonListItem, len(course.Lessons))
	for i, l := range course.Lessons {
		item := lessonListItem{
			ID:    l.ID,
			Title: l.Title,
			Type:  l.Type,
		}
		if isVIP && (l.Type == "vip" || l.Type == "demo") {
			item.Slug = slug.Generate(l.ID, claims.JTI, h.slugSecret)
		}
		lessons[i] = item
	}

	c.JSON(http.StatusOK, gin.H{
		"id":          course.ID,
		"title":       course.Title,
		"description": course.Description,
		"lessons":     lessons,
	})
}
