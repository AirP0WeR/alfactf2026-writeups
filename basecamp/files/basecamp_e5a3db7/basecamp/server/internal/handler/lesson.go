package handler

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"server/internal/auth"
	"server/internal/middleware"
	"server/internal/repository"
	"server/internal/slug"
)

type LessonHandler struct {
	lessonRepo *repository.LessonRepo
	auth       *auth.Service
	slugSecret string
	logger     *zap.Logger
}

func NewLessonHandler(
	lessonRepo *repository.LessonRepo,
	authService *auth.Service,
	slugSecret string,
	logger *zap.Logger,
) *LessonHandler {
	return &LessonHandler{
		lessonRepo: lessonRepo,
		auth:       authService,
		slugSecret: slugSecret,
		logger:     logger,
	}
}

func (h *LessonHandler) GetFreeLesson(c *gin.Context) {
	courseID, err := strconv.Atoi(c.Param("course_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректный ID курса"})
		return
	}
	lessonID, err := strconv.Atoi(c.Param("lesson_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректный ID урока"})
		return
	}

	lesson, err := h.lessonRepo.GetContent(c.Request.Context(), courseID, lessonID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Урок не найден"})
		return
	}

	if lesson.Type != "free" {
		c.JSON(http.StatusForbidden, gin.H{"error": "Этот урок доступен только VIP-пользователям"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"id":      lesson.ID,
		"title":   lesson.Title,
		"type":    lesson.Type,
		"content": lesson.Content,
	})
}

func (h *LessonHandler) RequestAccess(c *gin.Context) {
	claims := middleware.MustGetClaims(c)
	courseID, err := strconv.Atoi(c.Param("course_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректный ID курса"})
		return
	}
	lessonID, err := strconv.Atoi(c.Param("lesson_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректный ID урока"})
		return
	}

	lesson, err := h.lessonRepo.Get(c.Request.Context(), courseID, lessonID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Урок не найден"})
		return
	}

	if lesson.Type != "demo" {
		c.JSON(http.StatusForbidden, gin.H{"error": "Демо-доступ для этого урока недоступен"})
		return
	}

	tokenString, jti, err := h.auth.IssueToken(auth.TokenParams{
		UserID:   claims.Sub,
		Username: claims.Username,
		Role:     "vip",
		OneTime:  true,
		TTL:      10 * time.Second,
	})
	if err != nil {
		h.logger.Error("не удалось выпустить токен", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Внутренняя ошибка сервера"})
		return
	}

	lessonSlug := slug.Generate(lesson.ID, jti, h.slugSecret)

	c.JSON(http.StatusOK, gin.H{
		"token": tokenString,
		"slug":  lessonSlug,
	})
}

func (h *LessonHandler) GetVipLesson(c *gin.Context) {
	claims := middleware.MustGetClaims(c)
	courseID, err := strconv.Atoi(c.Param("course_id"))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Не найдено"})
		return
	}
	slugParam := c.Param("slug")

	lessonID, err := slug.Verify(slugParam, claims.JTI, h.slugSecret)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Не найдено"})
		return
	}

	lesson, err := h.lessonRepo.GetContent(c.Request.Context(), courseID, lessonID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Не найдено"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"id":      lesson.ID,
		"title":   lesson.Title,
		"type":    lesson.Type,
		"content": lesson.Content,
	})
}
