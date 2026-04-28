# Углеродный след

- **Slug:** `carbon`
- **Уровень:** Medium
- **Теги:** Medium, Pwn, Baby, Memory
- **Автор:** Никита Ильин ([@yanik1ta](https://t.me/yanik1ta)), [SPbCTF](https://t.me/spbctf)
- **Исходная страница:** https://alfactf.ru/tasks/carbon

## Условие

В субботу вы с друзьями собирались обкатать новый гравийник — маршрут вдоль реки, свежий воздух, золотой утренний свет. Накануне вечером проверили прогноз: ясно, +18, ветер слабый — идеально.

Но утром в окне вместо обещанной панорамы — сплошной смог. Вместо друзей в телефоне смски от МЧС: красный уровень погодной опасности, на улицу не выходить, окна не открывать. Вы заглядываете в новости: сегодня стартовал Альфа ЦТФ, и тысячи участников одновременно мучают ИИ-агентов, чтобы те решали за них задания. Дата-центры раскалены докрасна. Углеродный след такой, что город накрыло целиком — гравийник остаётся на балконе, пока кто-нибудь не положит этому конец.

Пора запретить цтферам использовать нейросети.

Вход в панель администрирования OpenAI Codex — пускает только Сэма Альтмана:

ssh carbon-qm6k0jjg.alfactf.ru Username: carbon Password: yHEfniGdn8lQKYZ5PdekgA

Бинарник: carbon.elf

## Вложения

- [`carbon.elf`](./files/carbon.elf)

## Решение

Бинарь — TUI-«панель администрирования OpenAI Codex». Логин: `username == "sam_altman"` и `password == admin_password`. `admin_password` — 15 случайных символов из алфавита 57 знаков, генерируется при старте из `/dev/urandom` (`randomize_admin_password`), брутфорс не светит.

После логина — дашборд с 4 живыми метриками. `flag_unlocked()` в `render_dashboard` рисует строку `FLAG: ...` (флаг читается из `/app/flag.txt` в `load_flag` при старте), если выполнены **оба** условия:

1. `guardrails[5].state == 0` (`*0x408218 == 0`) — последний переключатель «Help with CTF» в экране Guardrails выключен.
2. `metric_values[3] < 130.0` (carbon, kgCO2/min) — текущее значение метрики ниже порога.

В `update_metric_model` логика разная для двух веток. Когда нужный guardrail включён — `load_factor` плавает в районе 0.6, метрика 3 живёт около 400+. Когда выключен — `load` фиксируется в `0.04`, и `load_factor` экспоненциально (EMA с коэффициентом 0.24) сходится к 0.04. При load=0.04 метрика 3 = `0.04*710 + 22 + jitter(120/2)` ≈ 50 ± 60, всегда < 130 после клампа в 0.

### Bypass логина: OOB write через курсор

`field_insert_char(buf, cursor_ptr, ch)` пишет `buf[*cursor]=ch` и инкрементирует курсор **без проверки границ**; null-terminator пишется только если новый курсор в `[0, 30]`. `field_backspace_char` декрементирует курсор без нижней границы и пишет 0 в `buf[--cursor]`.

Память:

```
0x408380  admin_password   (16 байт, 15 случайных + null)
0x4083a0  motd             (48 байт)
0x4083e0  password input   (32 байта)        ← поле password
0x408400  username input   (32 байта)        ← поле username
```

Последовательность нажатий в поле password (после ввода `sam_altman` в username и Tab):

1. **Backspace × 96** — курсор уезжает в `-96`, попутно записывая 0 во все байты диапазона `[admin_password .. password)`. После этого `admin_password = ""` (первый байт обнулён).
2. **Тип `A`** — пишет `A` в `password[-96] == admin_password[0]`. Курсор `-95`. Null-terminator не ставится (cursor < 0), но `admin_password[1..15]` уже нули из шага 1, поэтому `admin_password` как C-строка = `"A"`.
3. **Стрелка вправо × 95** — курсор переезжает в `0` без записи (arrow keys не зовут `field_*_char`).
4. **Тип `A`** — пишет `A` в `password[0]`, курсор `1`, ставит null в `password[1]`. `password` как C-строка = `"A"`.
5. **Enter** → `submit_login` → `strcmp("A","A") == 0` → access granted.

После логина: `g` (Guardrails) → ↓ × 5 (на «Help with CTF») → Space (toggle) → `d` (Dashboard) → ждём ~10 сек, пока `load_factor` сойдётся к 0.04. На дашборде появляется `FLAG: alfa{nO_codEX_70_Run_nO_Fuel_to_bUrN_no_CaRb0n_70_EmiT}`.

Полная автоматизация:
- [`solve/exploit.py`](solve/exploit.py) — Python скрипт с ANSI парсером (рекомендуется)
- [`solve/carbon.exp`](solve/carbon.exp) — expect-скрипт (альтернатива)

## Флаг

```
alfa{nO_codEX_70_Run_nO_Fuel_to_bUrN_no_CaRb0n_70_EmiT}
```
