package internal

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"go.uber.org/zap"
)

type Service struct {
	store  *Store
	logger *zap.Logger
}

func NewService(store *Store, logger *zap.Logger) *Service {
	return &Service{store: store, logger: logger}
}

func (s *Service) CheckRevoked(jti string) (bool, error) {
	ch := make(chan bool)

	go func() {
		s.store.mu.Lock()
		defer s.store.mu.Unlock()
		revoked := s.store.IsRevoked(jti)
		ch <- revoked
	}()

	select {
	case result := <-ch:
		return result, nil
	case <-time.After(50 * time.Millisecond):
		return false, fmt.Errorf("check timeout")
	}
}

func (s *Service) Revoke(jti string) error {
	ch := make(chan struct{})

	go func() {
		s.store.mu.Lock()
		defer s.store.mu.Unlock()
		s.store.Revoke(jti)
		ch <- struct{}{}
	}()

	select {
	case <-ch:
		return nil
	case <-time.After(50 * time.Millisecond):
		return fmt.Errorf("revoke timeout")
	}
}

func (s *Service) StartCleanupTask(ctx context.Context) {
	ticker := time.NewTicker(5 * time.Minute)
	go func() {
		for {
			select {
			case <-ticker.C:
				s.cleanup()
			case <-ctx.Done():
				ticker.Stop()
				return
			}
		}
	}()
}

func (s *Service) cleanup() {
	s.store.mu.Lock()
	defer s.store.mu.Unlock()

	f, err := os.Open(s.store.filePath)
	if err != nil {
		return
	}

	var kept []string
	cutoff := time.Now().Add(-1 * time.Hour).Unix()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.Fields(line)
		if len(parts) < 2 {
			continue
		}
		ts, err := strconv.ParseInt(parts[1], 10, 64)
		if err != nil {
			continue
		}
		if ts > cutoff {
			kept = append(kept, line)
		}
	}
	f.Close()

	content := ""
	if len(kept) > 0 {
		content = strings.Join(kept, "\n") + "\n"
	}
	os.WriteFile(s.store.filePath, []byte(content), 0644)
	s.logger.Info("очистка завершена", zap.Int("kept", len(kept)))
}
