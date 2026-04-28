package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"server/internal/auth"
	"server/internal/revocation"
)

func AuthMiddleware(authService *auth.Service, revClient *revocation.Client, logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.Next()
			return
		}

		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		mapClaims, err := authService.ParseToken(tokenString)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Недействительный токен"})
			return
		}

		claims := ParseClaims(mapClaims)

		revoked, err := revClient.Check(c.Request.Context(), claims.JTI)
		if err != nil {
			logger.Error("не удалось проверить отзыв токена",
				zap.String("jti", claims.JTI),
				zap.Error(err),
			)
		} else if revoked {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Токен был отозван"})
			return
		}

		c.Set(claimsKey, claims)

		c.Next()

		if claims.OneTime {
			if err := revClient.Revoke(c.Request.Context(), claims.JTI); err != nil {
				logger.Error("не удалось отозвать one-time токен",
					zap.String("jti", claims.JTI),
					zap.Error(err),
				)
			}
		}
	}
}
