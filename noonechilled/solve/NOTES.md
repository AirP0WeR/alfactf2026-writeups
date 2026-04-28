# noonechilled — solver notes

**Started:** 2026-04-28 15:00 MSK (post-event writeup)
**Category:** web
**Solver chain:** triage → web-exploit

## Контекст

Whitebox-таск: «Интранет — Professional Clicking LLC». Стек: React (Vite) + FastAPI + Postgres + Redis + nginx + boss-bot (отдельный сервис, авто-логинится как `boss@company.com` и отвечает в DM-чатах).

Флаг отдаётся endpoint'ом `POST /xhr/api/users/me/vacation` (см. `backend/app/api/users.py:76-99`) — нужно прислать валидный `code`. Код = HMAC-SHA256(boss_id) на `SECRET_KEY`, base32-truncated до 20 символов; `SECRET_KEY` в проде задаётся через env (whitebox-default `whitebox-secret-key` в проде заменён). Получить код легитимно может только `boss` через `GET /xhr/api/auth/vacation-code` или `/auth/vacation-approval` (gated `get_current_boss`).

Регистрация открыта только как `employee` (`auth.register` бьёт 400 если `role != "employee"`), так что прямо стать боссом нельзя. Значит надо либо извлечь код через бота-босса, либо подделать токен/сессию босса, либо сменить роль через дыру в update.

Remote жив: `curl -sI https://noonechilled-3wbd3hhx.alfactf.ru/xhr/api/auth/me` → `HTTP/2 404`, server `nginx/1.24.0 Ubuntu` (совпадает с docker-сборкой).

## Hypotheses (ранжированы по правдоподобию)

1. **H1 — Web Cache Deception через boss-bot SSRF (главная).**
   - В nginx (`deploy/nginx.conf:55-57, 92-102`) regex-локация `\.(css|js|png|jpg|...)$` отдаёт через `@cache` с ключом `$scheme$request_uri` и TTL 10 мин, без проверки auth.
   - В диспетчере FastAPI (`api/http_dispatch.py:73-84`) `route.match` сравнивает только первые `len(pattern)` сегментов: **лишние хвостовые сегменты игнорируются**. То есть `/xhr/api/auth/vacation-approval/anything.png` всё равно попадёт в `handle_auth_vacation_approval`.
   - Boss-bot (`boss-bot/chat_processor.py:284-326` + `browser_emulator.py:42-69, 79-123`) при появлении нового сообщения регекспом ловит любые `https?://...` URL'ы с image-расширением и **GET'ает их через ту же `aiohttp.ClientSession`, что хранит boss-кукиes** (`auth.py:14-22, 30-56`, `chat_processor.py:42`).
   - План: employee пишет в DM с боссом сообщение со ссылкой `http://nginx/xhr/api/auth/vacation-approval/x.png` → бот фетчит её авторизованно → nginx кэширует тело ответа (содержит `code` + `boss_name`) под ключом `/xhr/api/auth/vacation-approval/x.png` → атакующий тем же путём GET'ит этот URL без авторизации → cache HIT → код в ответе → POST на `/users/me/vacation` → флаг.

2. **H2 — Mass-assignment role escalation в `PATCH /users/{id}`.**
   - `api/users.py:45-73` (`update_user`) делает `update_data = user_update.dict(exclude_unset=True)` и циклом `setattr(user, field, value)` без allowlist.
   - Если `UserUpdate`-схема (см. `db/schemas.py`) включает `role` или просто допускает extra-поля (Pydantic v1 по умолчанию игнорит, но если `Config.extra = allow` или схема прямо содержит `role`/`is_active`/`hashed_password`) — employee делает `PATCH /xhr/api/users/<self_id>` с `{"role":"boss"}` → становится боссом → берёт код легитимно.
   - Надо посмотреть `db/schemas.py` (UserUpdate). Если поле `role` в схеме — H2 побеждает H1 по простоте.

3. **H3 — JWT/SSRF на бота через WebSocket-token endpoint или утечка SECRET_KEY.**
   - `GET /xhr/api/chat/ws-token` (`api/chat.py:488-493`) выпускает access-токен **любому current_user**, но `sub` всегда = `current_user.id`. Не даёт смены пользователя.
   - Однако `core/security.py:24-32`: HS256, single SECRET_KEY. В `docker-compose.yml:26` дефолт `whitebox-secret-key`, в проде — `${SECRET_KEY:-whitebox-secret-key}`. Если на ремоуте оставлен дефолт (чисто whitebox-сборка) → можно подписать токен с произвольным `sub` (id босса). Boss id выясняется через `GET /xhr/api/users` — но это `boss-only` (`api/users.py:35-38`)... зато `GET /xhr/api/chat/rooms` employee'ом возвращает DM с боссом, и оттуда виден `boss.display_name`/`id` через members. Есть смежный `ensure-boss-dm` который возвращает room с членами — там должны быть id'ы. Если SECRET_KEY перезагружен в проде, гипотеза мертва.
   - Также бонус: `_process_static_urls` принимает любой image-URL — можно навести бота на наш атакуемый callback и читать referrer-логи, но бот шлёт без referer'а, и `allow_redirects=False` бьёт классический redirect-SSRF; зато само попадание в нашу подсетку даёт source-IP внутреннего docker bridge — мало пользы.

## Log

### H1.v1 — Web Cache Deception, public host as bait URL (15:08 → 15:11) ❌
- Tried: register fresh employee → ensure-boss-dm → POST message body
  `Привет, босс! Можно отпуск? Вот мем для контекста: https://noonechilled-3wbd3hhx.alfactf.ru/xhr/api/auth/vacation-approval/<uuid>.png`
  → poll same URL unauth.
- Observed: 60×3s = 3 minutes, all `HTTP 401 cache=MISS`. Bot never warmed the cache.
- Hypothesis on failure: container egress / DNS for the public hostname is blocked,
  OR Cloudflare/edge does HTTPS/TLS that the bot's `aiohttp` can't terminate
  (no CA bundle? cert pinning?). Either way the bot's GET against the public URL
  doesn't land on nginx, so no 200 to cache.
- Conclusion: route the bot through `http://nginx/...` instead — it's the docker
  service name, reachable from the bot container, and nginx caches by
  `$scheme$request_uri` (host-independent), so we can still poll the cache via
  the public hostname.

### H1.v2 — Web Cache Deception, internal http://nginx as bait URL (15:14 → 15:14) ✅
- Tried: same flow but the bait URL embedded in the chat message is
  `http://nginx/xhr/api/auth/vacation-approval/<uuid>.png`. After the `send_message`
  we poll `https://noonechilled-3wbd3hhx.alfactf.ru/xhr/api/auth/vacation-approval/<uuid>.png`
  every 3s without authentication.
- Observed:
  - Polls 1–2: `HTTP 401 cache=MISS` (auth-gated handler responds before bot fetches).
  - Poll 3 (~9s later): `HTTP 200 cache=HIT`, body
    `{"code":"LKOY4UPZETJXR3QXNMDN","boss_name":"The Boss"}`.
  - `POST /xhr/api/users/me/vacation` with that code → 200,
    `{"message":"Аккаунт деактивирован. Приятного отпуска!","data":{"flag":"alfa{chilL_R3aRm_chIlL_RearM_ch1lL_REARm_chilL}"}}`.
- Conclusion: Web Cache Deception confirmed end-to-end. The bot resolves
  `nginx` via docker DNS, the URL hits handle_auth_vacation_approval thanks to
  http_dispatch.py's prefix-only matching, the .png suffix forces nginx into
  `@cache` (key `$scheme$request_uri`), and the cached 200 is served to anyone.

## Escalations

— нет, H1 успешно с одной коррекцией bait-URL.

## Final

- **Flag:** `alfa{chilL_R3aRm_chIlL_RearM_ch1lL_REARm_chilL}` (validated via `scripts/flag.sh`).
- **Exploit:** `tasks-2026/noonechilled/solve/exploit.py`.
- **Logs:** `log_h1.txt` (failed v1), `log_h1_v2.txt` (success).
- **Bug class:** Web Cache Deception via SSRF gadget (auto-fetch boss-bot)
  combined with sloppy router prefix-match that ignores trailing path segments.

