# Никто, конечно, не чиллил

**Категория:** Web / Infra
**Сложность:** 🟡 Средняя (771 баллов, 21 решение)
**URL:** https://noonechilled-3wbd3hhx.alfactf.ru/
**Автор:** Лев Резниченко ([@mkvfaa](https://t.me/mkvfaa)), [SPbCTF](https://t.me/spbctf)
**Флаг:** `alfa{chilL_R3aRm_chIlL_RearM_ch1lL_REARm_chilL}`

> Решено пост-ивентом (CTF закончился 25 апреля 2026, решено 28 апреля 2026) — для полноты публичного сборника райтапов.

## Условие

Известный ведущий ведёт прямой репортаж откуда-то с вершины: «Это произошло среди дня. Холодный воздух бодрил, ветер трепал стропы палаток, внизу тянулись хвойные склоны. Казалось бы — идеальный момент, чтобы убрать телефон подальше и просто посмотреть вокруг. Но нет. Никто, конечно, не отдыхал. Все как один продолжали смотреть в экраны ноутбуков…»

Среди спальников, карабинов, термосов и рюкзаков люди открыли рабочие порталы и будто забыли, зачем вообще сюда выбрались. Помогите им хотя бы ненадолго выйти из режима вечного онлайна!

Исходники: `noonechilled_8fefca9.tar.gz`.

## Анализ системы

Whitebox-таск: интранет «Professional Clicking LLC». Стек:

- React (Vite) фронтенд
- FastAPI backend + Postgres + Redis
- nginx как reverse proxy с включённым `proxy_cache`
- Отдельный сервис **boss-bot** — автоматически логинится под `boss@company.com` и обрабатывает сообщения в DM

**Цель:** флаг возвращает `POST /xhr/api/users/me/vacation` (`backend/app/api/users.py:76-99`), которому нужен валидный `code`. Код = `HMAC-SHA256(boss_id, SECRET_KEY)` урезанный по base32 до 20 символов. Получить код можно только от лица босса через `GET /xhr/api/auth/vacation-code` или `GET /xhr/api/auth/vacation-approval` — оба эндпоинта закрыты `get_current_boss`.

Прямой подделки cookies/JWT не выходит, mass-assignment на `PATCH /users/{id}` зарезан Pydantic-схемой. Зато в системе есть три отдельных «недоработки», которые цепляются в полноценный **Web Cache Deception**.

### Уязвимость 1 — небрежный диспетчер в `api/http_dispatch.py:73-84`

```python
# (псевдокод сути)
segments = path.strip("/").split("/")
for pattern, handler in routes:
    if len(segments) >= len(pattern):
        if all(p == s or p.startswith(":") for p, s in zip(pattern, segments)):
            return handler(...)
```

Проверка `len(segments) >= len(pattern)` плюс `zip()` — это **префиксное совпадение**: лишние сегменты в конце пути молча отбрасываются. То есть `GET /xhr/api/auth/vacation-approval/<что-угодно>.png` диспатчится в тот же `handle_auth_vacation_approval`, что и `/xhr/api/auth/vacation-approval`. Хендлер всё равно требует `get_current_boss`, поэтому без авторизации просто 401 — но **формально путь стал «выглядеть как картинка»**.

### Уязвимость 2 — boss-bot автофетчит картинки из чата

`boss-bot/chat_processor.py:284-326` и `browser_emulator.py:42-69, 79-123`:

- Бот проходит по сообщениям в DM-комнатах регуляркой `https?://[^\s]+`.
- Для URL с расширениями `png|jpg|jpeg|gif|svg|ico|webp` делает GET через свой `aiohttp.ClientSession`.
- Эта сессия — та же, что используется при `boss@company.com` логине → внутри уже сидят все cookies босса (`auth.py:14-22, 30-56`).

Получается классический **SSRF-гаджет с авто-аутентификацией**: бот по нашему запросу идёт куда мы скажем (любой `http(s)://...`) и приносит туда полный куки-набор боссa. Ответ в чат не возвращается — бот фетчит «втихаря».

### Уязвимость 3 — nginx кэширует ответы по расширению, без auth-проверки

`deploy/nginx.conf:55-57, 92-102`:

```nginx
location ~* \.(css|js|png|jpg|jpeg|gif|svg|ico|webp|woff2?)$ {
    proxy_cache static_cache;
    proxy_cache_key $scheme$request_uri;
    proxy_cache_valid 200 10m;
    proxy_pass http://backend;
}
```

Регексп проверяет **только расширение в пути** — не `Content-Type` ответа, не наличие `Authorization`. Значит, если backend по какой-то причине отдал 200 на путь, заканчивающийся на `.png`, nginx сохранит тело **как есть** на 10 минут под ключом `$scheme$request_uri` (host-independent — важно дальше).

## Эксплуатация

Цепочка собирается так:

```
[1] Регистрируем employee
[2] Открываем DM с боссом (ensure-boss-dm)
[3] Шлём в DM сообщение с URL /xhr/api/auth/vacation-approval/<uuid>.png
[4] Бот фетчит этот URL аутентифицированно → backend отдаёт {"code","boss_name"} 200
[5] nginx видит ".png" в пути → кэширует ответ под request_uri
[6] Мы (без auth) GET'им тот же путь → cache HIT → читаем code
[7] POST /xhr/api/users/me/vacation с этим code → флаг
```

### Шаги пошагово

**1. Регистрация.** `POST /xhr/api/auth/register` с `role: "employee"` (другие роли отвергаются 400-кой).

**2. Открыть DM с боссом.** `POST /xhr/api/chat/rooms/ensure-boss-dm` — возвращает `room_id`, который мониторит boss-bot.

**3. Сообщение-приманка.**

```
http://nginx/xhr/api/auth/vacation-approval/<random-uuid>.png
```

В тексте сообщения добавляем русские ключевые слова («привет», «отпуск», «мем»), чтобы триггернуть `_should_respond` гарантированно — иначе только 30%-й шанс.

**4. Bot processing.** Регекс `https?://[^\s]+` ловит URL → `_process_static_urls` видит `.png` → `browser_emulator.GET("http://nginx/...")` через сессию босса. Диспатчер `http_dispatch.py` обрезает хвост, маршрутизирует на `handle_auth_vacation_approval`, тот возвращает `{"code":"<HMAC>","boss_name":"The Boss"}` 200 JSON. nginx по `.png` отправляет в `@cache` → запись лежит 10 минут.

**5. Опрос кэша без auth.**

```
GET https://noonechilled-3wbd3hhx.alfactf.ru/xhr/api/auth/vacation-approval/<uuid>.png
```

Тот же путь, но публичный хост. Cache key — `$scheme$request_uri` (хост в нём не участвует), поэтому попадаем в ту же кэш-запись. После ~9 секунд на 3-м опросе: `HTTP 200`, `X-Cache-Status: HIT`, тело `{"code":"LKOY4UPZETJXR3QXNMDN","boss_name":"The Boss"}`.

**6. Получение флага.**

```
POST /xhr/api/users/me/vacation
Content-Type: application/json
{"code": "LKOY4UPZETJXR3QXNMDN"}

→ {
  "message": "Аккаунт деактивирован. Приятного отпуска!",
  "data": {"flag": "alfa{chilL_R3aRm_chIlL_RearM_ch1lL_REARm_chilL}"}
}
```

### Pitfall: внутренний vs публичный хост в bait-URL

Первая попытка содержала в bait-URL публичный хост: `https://noonechilled-3wbd3hhx.alfactf.ru/xhr/api/auth/vacation-approval/<uuid>.png`. Опрос в течение ~3 минут возвращал только `401` с `X-Cache-Status: MISS`. Скорее всего фетч бота либо не прошёл из-за сетевой политики контейнера, либо упал на TLS-валидации.

Решение — указать в сообщении **внутреннее имя сервиса из docker-compose**: `http://nginx/xhr/api/auth/vacation-approval/<uuid>.png`. Бот достучался до nginx по http без TLS, ответ закэшировался. А поскольку cache key host-independent — мы продолжаем опрашивать через публичный URL и попадаем в ту же запись.

## Класс уязвимости

**Web Cache Deception** через SSRF-гаджет (auto-authenticated boss-bot), включённый небрежным префиксным диспатчером (молча принимает «псевдо-расширение» в хвосте) + nginx-кэш, который сохраняет auth-gated API-ответы только потому что URL заканчивается на `.png`.

Каждая из трёх ошибок по отдельности — мелкая. Соединённые в цепочку — leak HMAC и угон флага.

## Файлы

- [`solve/exploit.py`](solve/exploit.py) — самодостаточный эксплоит (register → ensure-boss-dm → bait → poll cache → claim flag).
- [`solve/NOTES.md`](solve/NOTES.md) — журнал гипотез (H1.v1 ❌ публичный хост, H1.v2 ✅ `http://nginx`).
- [`solve/log_h1.txt`](solve/log_h1.txt) — лог запросов неудачной попытки.
- [`solve/log_h1_v2.txt`](solve/log_h1_v2.txt) — лог успешной попытки.

## Ссылки

- [Web Cache Deception — PortSwigger](https://portswigger.net/web-security/web-cache-deception)
- Оригинальная статья: Omer Gil, *Web Cache Deception Attack* (2017)
- Релевантные файлы исходников: `boss-bot/chat_processor.py`, `boss-bot/browser_emulator.py`, `backend/app/api/http_dispatch.py`, `deploy/nginx.conf`
