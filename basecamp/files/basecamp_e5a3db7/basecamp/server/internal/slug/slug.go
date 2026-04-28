package slug

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"strconv"
	"strings"
)

func Generate(lessonID int, jti string, secret string) string {
	data := fmt.Sprintf("%d:%s", lessonID, jti)

	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(data))
	signature := mac.Sum(nil)

	raw := fmt.Sprintf("%d:%x", lessonID, signature)
	return base64.RawURLEncoding.EncodeToString([]byte(raw))
}

func Verify(slug string, jti string, secret string) (int, error) {
	raw, err := base64.RawURLEncoding.DecodeString(slug)
	if err != nil {
		return 0, fmt.Errorf("invalid slug")
	}

	parts := strings.SplitN(string(raw), ":", 2)
	if len(parts) != 2 {
		return 0, fmt.Errorf("invalid slug format")
	}

	lessonID, err := strconv.Atoi(parts[0])
	if err != nil {
		return 0, fmt.Errorf("invalid lesson id")
	}

	receivedSig := parts[1]

	data := fmt.Sprintf("%d:%s", lessonID, jti)
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(data))
	expectedSig := fmt.Sprintf("%x", mac.Sum(nil))

	if !hmac.Equal([]byte(receivedSig), []byte(expectedSig)) {
		return 0, fmt.Errorf("signature mismatch")
	}

	return lessonID, nil
}
