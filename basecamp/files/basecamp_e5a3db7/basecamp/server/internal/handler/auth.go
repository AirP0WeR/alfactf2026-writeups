package handler

import (
	"net/http"
	"regexp"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"server/internal/auth"
	"server/internal/middleware"
	"server/internal/repository"
	"server/internal/revocation"
)

type AuthHandler struct {
	userRepo  *repository.UserRepo
	auth      *auth.Service
	revClient *revocation.Client
	logger    *zap.Logger
}

func NewAuthHandler(userRepo *repository.UserRepo, authService *auth.Service, revClient *revocation.Client, logger *zap.Logger) *AuthHandler {
	return &AuthHandler{
		userRepo:  userRepo,
		auth:      authService,
		revClient: revClient,
		logger:    logger,
	}
}

var usernameRegex = regexp.MustCompile(`^[a-zA-Z0-9_]+$`)

type authRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func (h *AuthHandler) Register(c *gin.Context) {
	var req authRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректный запрос"})
		return
	}

	if len(req.Username) < 9 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Имя пользователя должно содержать минимум 9 символов"})
		return
	}
	if !usernameRegex.MatchString(req.Username) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Имя пользователя может содержать только латинские буквы, цифры и _"})
		return
	}
	if len(req.Password) < 9 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Пароль должен содержать минимум 9 символов"})
		return
	}

	existing, err := h.userRepo.GetByUsername(c.Request.Context(), req.Username)
	if err != nil {
		h.logger.Error("ошибка при проверке пользователя", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Внутренняя ошибка сервера"})
		return
	}
	if existing != nil {
		c.JSON(http.StatusConflict, gin.H{"error": "Пользователь с таким именем уже существует"})
		return
	}

	hash, err := auth.HashPassword(req.Password)
	if err != nil {
		h.logger.Error("ошибка хеширования пароля", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Внутренняя ошибка сервера"})
		return
	}

	if err := h.userRepo.Create(c.Request.Context(), req.Username, hash); err != nil {
		h.logger.Error("ошибка создания пользователя", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Внутренняя ошибка сервера"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Регистрация прошла успешно"})
}

func (h *AuthHandler) Login(c *gin.Context) {
	var req authRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректный запрос"})
		return
	}

	if len(req.Password) < 9 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Пароль должен содержать минимум 9 символов"})
		return
	}

	user, err := h.userRepo.GetByUsername(c.Request.Context(), req.Username)
	if err != nil {
		h.logger.Error("ошибка при получении пользователя", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Внутренняя ошибка сервера"})
		return
	}
	if user == nil || !auth.CheckPassword(req.Password, user.PasswordHash) {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Неверное имя пользователя или пароль"})
		return
	}

	token, _, err := h.auth.IssueToken(auth.TokenParams{
		UserID:   user.ID,
		Username: user.Username,
		Role:     user.Role,
		TTL:      24 * time.Hour,
	})
	if err != nil {
		h.logger.Error("ошибка выпуска токена", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Внутренняя ошибка сервера"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"token": token})
}

func (h *AuthHandler) Logout(c *gin.Context) {
	claims := middleware.MustGetClaims(c)

	if err := h.revClient.Revoke(c.Request.Context(), claims.JTI); err != nil {
		h.logger.Warn("не удалось отозвать токен при logout",
			zap.String("jti", claims.JTI),
			zap.Error(err),
		)
	}

	c.JSON(http.StatusOK, gin.H{"message": "Вы вышли из системы"})
}
