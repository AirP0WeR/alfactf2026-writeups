# Новая куртка

- **Slug:** `newjacket`
- **Уровень:** Простые
- **Теги:** Easy, Infra, Linux, SSH
- **Автор:** Владимир Лебедев ([@KillingInTheNameOf](https://t.me/KillingInTheNameOf)), [SPbCTF](https://t.me/spbctf)
- **Исходная страница:** https://alfactf.ru/tasks/newjacket

## Условие

Хайповый бренд горпкор-одежды запускает закрытые продажи новой куртки и обещает, что доступ будет только для своих — через внутренний сервер с двухфакторной аутентификацией.

Проблема в том, что куртка вам нужна, а вот слушать ещё неделю, как какой-то тип с аватаркой из спешалти-кофейни рассказывает про важность многослойной одежды, вы не готовы. Оформите заказ на куртку раньше ушлых перекупов.

```
ssh newjacket-w9gzrloh.alfactf.ru
Username: newjacket
Password: oQBMySPu8ywD9aDuCIwGlg
```

Система защиты: `home_newjacket_.bashrc` — после ssh-логина исполняется такая «2FA»:

```bash
export EDITOR=/usr/bin/vim

old_stty=$(stty -g)
stty intr undef quit undef susp undef

echo 'Type the one-time password.'
read -e -s -r -p 'One-time password: ' otp

stty "$old_stty"

if [[ "$otp" == "[REDACTED]" ]]; then
  echo 'OTP accepted.'
  return
fi

echo '2FA failed.'
logout >/dev/null 2>&1 || exit 1
```

## Решение

Ключевые детали скрипта:

- `stty intr undef quit undef susp undef` — отключает только Ctrl+C / Ctrl+\ / Ctrl+Z. На readline-биндинги это не влияет.
- `read -e` — включает readline-редактирование вводимой строки.
- В readline есть стандартный биндинг **`Ctrl+X Ctrl+E`** (`edit-and-execute-command`) — он сохраняет текущий буфер во временный файл и открывает его в `$EDITOR`.
- `EDITOR=/usr/bin/vim` любезно подставлен скриптом. А из vim тривиально вырваться в шелл через `:!cmd` — это происходит **до** проверки `[[ "$otp" == ... ]]`, т.е. в обход 2FA.

Шаги:

1. SSH-логин.
2. На промпте `One-time password:` нажать `Ctrl+X`, затем `Ctrl+E` (не отпуская Ctrl) — откроется vim.
3. В vim выполнить `:!sh -c '…'` (или `:!/bin/bash` для интерактивного шелла).
4. Прочитать `/home/newjacket/flag.txt`.

Полный автомат — [`solve/jacket.exp`](solve/jacket.exp) (expect-скрипт).

## Флаг

```
alfa{C7Rl_x_CTrL_e_IS_A_5H3Ll}
```
