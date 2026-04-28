package middleware

import (
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

const claimsKey = "claims"

type Claims struct {
	Sub      int
	Username string
	Role     string
	JTI      string
	OneTime  bool
	Exp      int64
}

func GetClaims(c *gin.Context) (*Claims, bool) {
	val, exists := c.Get(claimsKey)
	if !exists {
		return nil, false
	}
	claims, ok := val.(*Claims)
	return claims, ok
}

func MustGetClaims(c *gin.Context) *Claims {
	claims, ok := GetClaims(c)
	if !ok {
		panic("claims not found in context")
	}
	return claims
}

func ParseClaims(m jwt.MapClaims) *Claims {
	claims := &Claims{}
	if v, ok := m["sub"].(float64); ok {
		claims.Sub = int(v)
	}
	if v, ok := m["username"].(string); ok {
		claims.Username = v
	}
	if v, ok := m["role"].(string); ok {
		claims.Role = v
	}
	if v, ok := m["jti"].(string); ok {
		claims.JTI = v
	}
	if v, ok := m["one_time"].(bool); ok {
		claims.OneTime = v
	}
	if v, ok := m["exp"].(float64); ok {
		claims.Exp = int64(v)
	}
	return claims
}
