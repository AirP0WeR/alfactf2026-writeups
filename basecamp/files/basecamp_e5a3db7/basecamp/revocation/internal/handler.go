package internal

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type Handler struct {
	service *Service
	logger  *zap.Logger
}

func NewHandler(service *Service, logger *zap.Logger) *Handler {
	return &Handler{service: service, logger: logger}
}

func (h *Handler) Check(c *gin.Context) {
	var req struct {
		JTI string `json:"jti" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Поле jti обязательно"})
		return
	}

	revoked, err := h.service.CheckRevoked(req.JTI)
	if err != nil {
		h.logger.Error("ошибка проверки отзыва", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Внутренняя ошибка"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"revoked": revoked})
}

func (h *Handler) Revoke(c *gin.Context) {
	var req struct {
		JTI string `json:"jti" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Поле jti обязательно"})
		return
	}

	if err := h.service.Revoke(req.JTI); err != nil {
		h.logger.Error("ошибка отзыва токена", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Внутренняя ошибка"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"ok": true})
}

func (h *Handler) Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
