package revocation

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"go.uber.org/zap"
)

const (
	requestTimeout = 5 * time.Second
	maxAttempts    = 3
	retryBackoff   = 200 * time.Millisecond
)

type Client struct {
	baseURL    string
	httpClient *http.Client
	logger     *zap.Logger
}

func NewClient(baseURL string, logger *zap.Logger) *Client {
	return &Client{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: requestTimeout,
			Transport: &http.Transport{
				MaxIdleConns:        500,
				MaxIdleConnsPerHost: 500,
				MaxConnsPerHost:     500,
				IdleConnTimeout:     90 * time.Second,
			},
		},
		logger: logger,
	}
}

func (c *Client) doWithRetry(ctx context.Context, path string, payload []byte) ([]byte, error) {
	var lastErr error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		body, err := c.attempt(ctx, path, payload)
		if err == nil {
			return body, nil
		}
		lastErr = err
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		if attempt < maxAttempts {
			select {
			case <-time.After(retryBackoff):
			case <-ctx.Done():
				return nil, ctx.Err()
			}
		}
	}
	return nil, lastErr
}

func (c *Client) attempt(ctx context.Context, path string, payload []byte) ([]byte, error) {
	reqCtx, cancel := context.WithTimeout(ctx, requestTimeout)
	defer cancel()

	req, err := http.NewRequestWithContext(reqCtx, http.MethodPost, c.baseURL+path, bytes.NewReader(payload))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("revocation-service недоступен: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("revocation-service вернул %d", resp.StatusCode)
	}
	return io.ReadAll(resp.Body)
}

func (c *Client) Check(ctx context.Context, jti string) (bool, error) {
	payload, _ := json.Marshal(map[string]string{"jti": jti})
	body, err := c.doWithRetry(ctx, "/check", payload)
	if err != nil {
		return false, err
	}
	var result struct {
		Revoked bool `json:"revoked"`
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return false, fmt.Errorf("revocation-service вернул некорректный ответ: %w", err)
	}
	return result.Revoked, nil
}

func (c *Client) Revoke(ctx context.Context, jti string) error {
	payload, _ := json.Marshal(map[string]string{"jti": jti})
	_, err := c.doWithRetry(ctx, "/revoke", payload)
	return err
}
