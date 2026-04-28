package main

import (
	"context"
	"os"
	"os/signal"
	"syscall"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"revocation/internal"
)

func envOrDefault(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func main() {
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	dataFile := envOrDefault("DATA_FILE", "/data/revoked.txt")
	port := envOrDefault("PORT", "8081")

	store := internal.NewStore(dataFile, logger)
	service := internal.NewService(store, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	service.StartCleanupTask(ctx)

	handler := internal.NewHandler(service, logger)

	r := gin.New()
	r.Use(gin.Recovery())

	r.POST("/check", handler.Check)
	r.POST("/revoke", handler.Revoke)
	r.GET("/health", handler.Health)

	logger.Info("revocation-service запущен", zap.String("port", port))

	go func() {
		if err := r.Run(":" + port); err != nil {
			logger.Fatal("ошибка запуска сервера", zap.Error(err))
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	cancel()
	logger.Info("revocation-service остановлен")
}
