#!/bin/bash
BASE=https://peakmood-ou1mhzjv.alfactf.ru
DEV=$(uuidgen)
echo "device_id=$DEV"

echo "--- /api/v1/session/open ---"
TOK=$(curl -s -X POST "$BASE/api/v1/session/open" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"device_id\":\"$DEV\",\"client_version\":\"1.0.0\",\"model\":\"Pixel\"}" | tee /dev/stderr | jq -r .session_token)
echo "TOK=$TOK"
