package internal

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"sync"
	"time"

	"go.uber.org/zap"
)

type Store struct {
	mu       sync.Mutex
	filePath string
	logger   *zap.Logger
}

func NewStore(filePath string, logger *zap.Logger) *Store {
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		os.WriteFile(filePath, []byte{}, 0644)
	}
	return &Store{filePath: filePath, logger: logger}
}

func (s *Store) IsRevoked(jti string) bool {
	f, err := os.Open(s.filePath)
	if err != nil {
		return false
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		parts := strings.Fields(scanner.Text())
		if len(parts) >= 1 && parts[0] == jti {
			return true
		}
	}
	return false
}

func (s *Store) Revoke(jti string) {
	f, err := os.OpenFile(s.filePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		s.logger.Error("не удалось открыть файл для записи", zap.Error(err))
		return
	}
	defer f.Close()

	entry := fmt.Sprintf("%s %d\n", jti, time.Now().Unix())
	f.WriteString(entry)
}
