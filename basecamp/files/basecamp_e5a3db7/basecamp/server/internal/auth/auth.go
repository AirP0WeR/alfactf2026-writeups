package auth

import (
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

type Service struct {
	jwtSecret string
}

func NewService(jwtSecret string) *Service {
	return &Service{jwtSecret: jwtSecret}
}

type TokenParams struct {
	UserID   int
	Username string
	Role     string
	OneTime  bool
	TTL      time.Duration
}

func (s *Service) IssueToken(p TokenParams) (string, string, error) {
	jti := uuid.New().String()

	claims := jwt.MapClaims{
		"sub":      p.UserID,
		"username": p.Username,
		"role":     p.Role,
		"jti":      jti,
		"iat":      time.Now().Unix(),
		"exp":      time.Now().Add(p.TTL).Unix(),
	}

	if p.OneTime {
		claims["one_time"] = true
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signed, err := token.SignedString([]byte(s.jwtSecret))
	if err != nil {
		return "", "", err
	}

	return signed, jti, nil
}

func (s *Service) ParseToken(tokenString string) (jwt.MapClaims, error) {
	token, err := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
		}
		return []byte(s.jwtSecret), nil
	})
	if err != nil {
		return nil, err
	}
	if !token.Valid {
		return nil, fmt.Errorf("invalid token")
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, fmt.Errorf("invalid claims")
	}

	return claims, nil
}

func HashPassword(password string) (string, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hash), nil
}

func CheckPassword(password, hash string) bool {
	return bcrypt.CompareHashAndPassword([]byte(hash), []byte(password)) == nil
}
