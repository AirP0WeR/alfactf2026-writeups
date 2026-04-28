# Диджитал-рюкзак

- **Slug:** `backpack`
- **Уровень:** Medium
- **Теги:** Medium, Crypto
- **Автор:** Антон Леевик ([@f_o_rest](https://t.me/f_o_rest)), [SPbCTF](https://t.me/spbctf)
- **Исходная страница:** https://alfactf.ru/tasks/backpack

## Условие

"Nothing beats a Digital Backpack! And right now you can save 50 pounds per person !"

Диджитал-рюкзак — новое приспособление для всех хайкеров, защищённое от всех хакеров. В него можно сложить не только обычные вещи, но и свои данные в шифрованном виде. Подключайте флешку и пакуйте в рюкзак все нужные файлы, чтобы удобно их переносить.

Ваш товарищ недавно купил этот рюкзак, но тот невовремя обновился, и теперь он не может достать свои данные. Помогите ему!

nc backpack-t32vei5w.alfactf.ru 30034 Unzip the backpack: 6D5LCc1QprneFFb5adiPOQ

Исходный код: backpack_398b99e.tar.gz

## Вложения

- [`backpack_398b99e.tar.gz`](./files/backpack_398b99e.tar.gz)

## Наблюдения

- Название «backpack» отсылает к рюкзаку хайкера; CTF-слово «backpack» также используется для knapsack/subset-sum криптосистем. Это ложная дорожка — задача про AES, не про knapsack.
- Plaintext флага — не просто `alfa{5hIrOkA_R3K4_GluBoka_r3k4}`, а тематический текст-«VIP билет» на концерт Надежды Кадышевой, содержащий флаг внутри. Слова `шИРОКА РЕКА` в флаге — отсылка к её известной песне.
- Сервер **геоблочит** часть IP-диапазонов: локальный Mac тайм-аутит, с нашего VPS в Финляндии коннект мгновенный.
- Ключ генерируется заново на каждое TCP-соединение — вся атака (все ~96 × 256 + disambiguation запросов) должна уложиться в одну сессию.
- Без `--save` промежуточный plaintext при обрыве теряется безвозвратно. Поэтому `--save` обязателен.

## Решение

### 1. Анализ исходников

`files/backpack_398b99e/backpack/src/`:

- `server.c` — при старте вызывает `store_legacy_flag`: шифрует строку `FLAG_CONTENT` через `aes_encrypt_cbc` **без gzip-обёртки** и кладёт в blob-хранилище.
- `crypto.c` — AES-128-CBC через OpenSSL EVP; `g_session_key` = 16 свежих байт из `/dev/urandom` **на каждый коннект**.
- `storage.c` — blob storage по случайному hex id; имя файла выводится из `decrypt_first_two_blocks` (первые два блока, padding=0 — т.е. зашифрованного gzip-header). Если первые байты не дают валидного имени, файл получает имя `unknown_file_N`.
- `gzip.c` — строгая валидация gzip-заголовка `1f 8b 08 08 ...`.
- `common.h` — `AES_BLOCK_SIZE=16`.

### 2. Уязвимость — PKCS#7 padding oracle

Команда `get <name>` запускает pipeline:

```
aes_decrypt_cbc(PKCS#7 check) → inspect_gzip_header → gzip_decompress
```

Ответы клиенту:

| Состояние | Ответ |
|---|---|
| Плохой PKCS#7 | `error: failed to decrypt 'name'` |
| Хороший PKCS#7, плохой gzip | `error: <gzip_error_string>` |
| Хороший PKCS#7, хороший gzip, плохой inflate | `error: decompression failed` |

Подстрока `failed to decrypt` присутствует **только** в первом случае → однобитовый оракул.

### 3. Workflow одного запроса к оракулу

```
put-raw 32          # IV' (16 байт) || target_ct (16 байт)
ls                  # видим 2 файла: флаг (96B) и наш blob (32B)
get-raw <name>      # по размеру определяем, какое имя наше
get <my_name>       # оракул: есть/нет "failed to decrypt"
rm <my_name>        # cleanup, чтобы счётчик unknown_file_N не рос
```

Файлы сортируются по hex id (qsort в `collect_file_entries`), поэтому наш blob может быть `unknown_file_1` или `unknown_file_2` — disambiguate по размеру через `get-raw`.

### 4. Атака (стандартный CBC padding oracle)

Флаг: 96 байт ciphertext = IV (16B) + 6 блоков × 16B.

Для каждого блока `C[i]` восстанавливаем `intermediate[j]` — промежуточное состояние после AES block decrypt. Перебираем 256 вариантов байта `iv'[j]`, ищем `iv'[j] ^ intermediate[j] == pad_byte`. Затем `plaintext[j] = intermediate[j] ^ prev_ct[j]`.

Disambiguate при `pad_byte=1`: если нашли OK-байт, проверяем с флипнутым `iv'[j-1]` — если OK пропал, значит настоящий padding был `\x02\x02...` (false positive), пропускаем и идём дальше.

### 5. Запуск

**Локальный sanity (docker):**

```bash
cd tasks-2026/backpack/files/backpack_398b99e/backpack && docker compose up -d --build
cd ../../.. && python3 solve/solve.py --host 127.0.0.1 --port 30034 --block 1
# Block 1 = b'VIP ticket to Na'  (~12s)
```

**Удалённо с VPS (геоблок обходится через Финляндию):**

```bash
scp tasks-2026/backpack/solve/solve.py root@204.168.133.116:/root/backpack_solve.py
scripts/srv.sh 01 "nohup python3 /root/backpack_solve.py \
    --host backpack-t32vei5w.alfactf.ru --port 30034 \
    --save /root/backpack_pt.bin > /root/backpack_run.log 2>&1 &"

# мониторинг:
scripts/srv.sh 01 "tail -25 /root/backpack_run.log; xxd /root/backpack_pt.bin"

# выкачать результат:
scp root@204.168.133.116:/root/backpack_pt.bin tasks-2026/backpack/artifacts/pt.bin
```

**Метрики:** ~90–130s/блок на srv-01, 6 блоков × ~120s ≈ 10.5 минут. ~4096 oracle-запросов на блок (256 × 16 + disambiguation).

Скрипт: [`solve/solve.py`](./solve/solve.py) — pwntools, класс `Backpack`, функция `attack_one_block`. Опции `--block N`, `--from-block N`, `--save <file>`.

### 6. Извлечение флага

```
Full plaintext (112B с padding):
b'VIP ticket to Nadezhda Kadysheva\'s concert. Date: April 25, 7:00 PM. '
b'Location: alfa{5hIrOkA_R3K4_GluBoka_r3k4}.\x0f\x0f\x0f...'
```

PKCS#7 unpad (pad byte `\x0f` = 15 × 0x0f), grep `alfa{` → флаг.

## Флаг

```
alfa{5hIrOkA_R3K4_GluBoka_r3k4}
```
