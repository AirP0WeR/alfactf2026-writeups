# 🐱 cat

<div align="center">

![Category](https://img.shields.io/badge/Категория-WEB-blue?style=for-the-badge)
![Difficulty](https://img.shields.io/badge/Сложность-Лёгкая-success?style=for-the-badge)

**Чит-коды в веб-консоли + обход DOM защиты**

</div>

---

## 📋 Информация о задаче

| Поле | Значение |
|-------|-------|
| **🏷️ Название** | cat |
| **📂 Категория** | Web |  
| **📊 Сложность** | 🟢 Лёгкая |
| **🏷️ Tags** | `Clientside` `Baby` `JavaScript` |
| **👤 Author** | Никита Ильин ([@yanik1ta](https://t.me/yanik1ta)), SPbCTF |
| **🔗 URL** | [cat-k4sl0sey.alfactf.ru](https://cat-k4sl0sey.alfactf.ru/) |

---

## 📖 Description

> Сегодня в автобусе, пока ехал на трейл, я встретил кота!
>
> Представляешь, сидит один у окошка в наушниках и ритмично качает мордочкой. Не знаю, что он слушает, но я решил его взять с собой на трейл — а потом отнести в рюкзаке обратно в город.

---

## 🔍 Анализ

При открытии страницы видим **Three.js runner game** с боковой панелью "Чит-коды". В панели есть:

```html
<canvas class="cheat-copy-canvas">  <!-- Чит-коды нарисованы здесь -->
<span class="cheat-cover">Осталось камней: 500</span>  <!-- Перекрывает canvas -->
```

### 🛡️ Protection Mechanisms

Защита от чтения чит-кодов **полностью клиентская**:

1. **CSS Blur Filter**: `filter: blur(9px)` на canvas — текст размыт
2. **DOM Overlay**: `.cheat-cover` элемент физически закрывает часть чит-кодов

---

## ⚡ Exploitation

### Step 1: Remove Client-Side Protection

Открываем **DevTools Console** и снимаем защиту:

```javascript
// Убираем размытие
document.querySelector('.cheat-copy-canvas').style.filter = 'none';

// Скрываем перекрывающий элемент  
document.querySelector('.cheat-cover').style.display = 'none';
```

### Step 2: Extract Cheat Codes

После снятия защиты на canvas становятся видны чит-коды:

- **🏃‍♂️ FASTER:** `catcatcat`
- **🛡️ GODMODE:** `powerup`

### Step 3: Activate Cheats

Вводим коды **прямо с клавиатуры** (игра слушает `keydown` события):

1. Набираем `catcatcat` → включается ускорение
2. Набираем `powerup` → включается бессмертие  

### Step 4: Win & Get Flag

С читами легко достигаем **максимального результата**. При достижении 100% появляется **жёлтый баннер с флагом**.

---

## 🚩 Flag

```
alfa{music_cat_in_a_backpack}
```

> **💡 Flag Origin:** Отсылка к условию — кот с наушниками (music) в автобусе, которого взяли в рюкзаке (backpack) на трейл.

---

## 📎 Artifacts  

<details>
<summary>📁 Files Generated During Exploitation</summary>

- `artifacts/index.html` — Original HTML with boot-loader
- `artifacts/rendered.html` — DOM after React mounting (shows cheat elements)  
- `artifacts/index-BREGg8EB.css` — CSS styles (`.cheat-panel.unlocked` proof)
- `artifacts/index.js` — Minified bundle (1MB, three.js + game logic)
- `solve/capture_requests.py` — Playwright automation script

</details>

---

<div align="center">

**🎯 Total Time:** ~5 minutes | **💡 Key Insight:** Client-side security ≠ security

[← Back to Index](../README.md)

</div>
