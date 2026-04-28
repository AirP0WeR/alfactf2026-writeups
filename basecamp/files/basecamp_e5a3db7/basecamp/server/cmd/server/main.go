package main

import (
	"database/sql"
	"errors"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"

	"github.com/gin-gonic/gin"
	"github.com/golang-migrate/migrate/v4"
	migratesqlite "github.com/golang-migrate/migrate/v4/database/sqlite"
	_ "github.com/golang-migrate/migrate/v4/source/file"
	"go.uber.org/zap"
	_ "modernc.org/sqlite"

	"server/internal/auth"
	"server/internal/handler"
	"server/internal/middleware"
	"server/internal/repository"
	"server/internal/revocation"
)

func envOrDefault(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func mustEnv(key string) string {
	v := os.Getenv(key)
	if v == "" {
		panic("required env var not set: " + key)
	}
	return v
}

func openDB(dbPath string, logger *zap.Logger) *sql.DB {
	if err := os.MkdirAll(filepath.Dir(dbPath), 0o755); err != nil {
		logger.Fatal("не удалось создать каталог для БД", zap.Error(err))
	}
	dsn := dbPath + "?_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)&_pragma=foreign_keys(1)"
	database, err := sql.Open("sqlite", dsn)
	if err != nil {
		logger.Fatal("не удалось открыть БД", zap.Error(err))
	}
	if err := database.Ping(); err != nil {
		logger.Fatal("БД не отвечает", zap.Error(err))
	}
	database.SetMaxOpenConns(1)
	return database
}

func runMigrations(database *sql.DB, migrationsDir string, logger *zap.Logger) {
	driver, err := migratesqlite.WithInstance(database, &migratesqlite.Config{})
	if err != nil {
		logger.Fatal("не удалось инициализировать драйвер миграций", zap.Error(err))
	}
	m, err := migrate.NewWithDatabaseInstance("file://"+migrationsDir, "sqlite", driver)
	if err != nil {
		logger.Fatal("не удалось создать migrate", zap.Error(err))
	}
	if err := m.Up(); err != nil && !errors.Is(err, migrate.ErrNoChange) {
		logger.Fatal("ошибка применения миграций", zap.Error(err))
	}
	logger.Info("миграции применены")
}

func registerStatic(r *gin.Engine, webRoot string, logger *zap.Logger) {
	if _, err := os.Stat(webRoot); err != nil {
		logger.Warn("каталог со статикой недоступен", zap.String("path", webRoot), zap.Error(err))
		return
	}
	indexPath := filepath.Join(webRoot, "index.html")

	r.NoRoute(func(c *gin.Context) {
		urlPath := c.Request.URL.Path
		if strings.HasPrefix(urlPath, "/api/") {
			c.AbortWithStatusJSON(http.StatusNotFound, gin.H{"error": "Не найдено"})
			return
		}
		clean := filepath.Clean("/" + urlPath)
		candidate := filepath.Join(webRoot, clean)
		if !strings.HasPrefix(candidate, webRoot) {
			c.File(indexPath)
			return
		}
		if info, err := os.Stat(candidate); err == nil && !info.IsDir() {
			c.File(candidate)
			return
		}
		c.File(indexPath)
	})
}

func main() {
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	dbPath := mustEnv("DATABASE_URL")
	jwtSecret := mustEnv("JWT_SECRET")
	slugSecret := mustEnv("SLUG_SECRET")
	migrationsDir := envOrDefault("MIGRATIONS_DIR", "/usr/local/share/basecamp/migrations")
	webRoot := envOrDefault("WEB_ROOT", "/srv/web")
	revocationURL := envOrDefault("REVOCATION_URL", "http://127.0.0.1:8081")
	port := envOrDefault("PORT", "8080")

	database := openDB(dbPath, logger)
	defer database.Close()
	logger.Info("подключение к БД установлено", zap.String("path", dbPath))

	runMigrations(database, migrationsDir, logger)

	authService := auth.NewService(jwtSecret)
	revClient := revocation.NewClient(revocationURL, logger)

	userRepo := repository.NewUserRepo(database)
	courseRepo := repository.NewCourseRepo(database)
	lessonRepo := repository.NewLessonRepo(database)

	authHandler := handler.NewAuthHandler(userRepo, authService, revClient, logger)
	courseHandler := handler.NewCourseHandler(courseRepo, slugSecret, logger)
	lessonHandler := handler.NewLessonHandler(lessonRepo, authService, slugSecret, logger)

	authMw := middleware.AuthMiddleware(authService, revClient, logger)

	r := gin.New()
	r.Use(gin.Recovery())

	api := r.Group("/api")

	api.POST("/auth/register", authHandler.Register)
	api.POST("/auth/login", authHandler.Login)
	api.GET("/courses", courseHandler.ListCourses)

	withOptionalAuth := api.Group("")
	withOptionalAuth.Use(authMw)
	{
		withOptionalAuth.GET("/courses/:course_id", courseHandler.GetCourse)
		withOptionalAuth.GET("/courses/:course_id/lessons/:lesson_id", lessonHandler.GetFreeLesson)
	}

	withAuth := api.Group("")
	withAuth.Use(authMw, middleware.RequireRole("user", "vip"))
	{
		withAuth.POST("/auth/logout", authHandler.Logout)
		withAuth.POST("/courses/:course_id/lessons/:lesson_id/request-access", lessonHandler.RequestAccess)
	}

	vipContent := api.Group("")
	vipContent.Use(authMw, middleware.RequireRole("vip"))
	{
		vipContent.GET("/courses/:course_id/lessons/access/:slug", lessonHandler.GetVipLesson)
	}

	registerStatic(r, webRoot, logger)

	logger.Info("server запущен", zap.String("port", port))

	go func() {
		if err := r.Run(":" + port); err != nil {
			logger.Fatal("ошибка запуска сервера", zap.Error(err))
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("server остановлен")
}
