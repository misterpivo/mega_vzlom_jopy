<div align="center">

# 📘 AI OCR Tray Bot

### ✨ Розумний асистент для тестів, задач і коду — з OCR, Gemini 2.5 у системному треї
</div>

---

## 🎯 Опис

**AI OCR Tray Bot** — це легка фонова утиліта для Windows і macOS, яка:

- 📸 **робить OCR усього екрана**
- 🤖 **надсилає розпізнаний текст у Gemini 2.5 Pro**
- 🅰 **показує правильний варіант відповіді прямо в іконці трея**
- 💻 **уміє працювати з кодом і текстами**
- 📎 **дозволяє скопіювати відповідь одним натисканням**
- 🔒 **має блокування гарячих клавіш**
- ❌ **і завершення через меню трея**

> Програма працює у фоні, майже не навантажує систему й керується гарячими клавішами.

---

## ✨ Функціонал

### 📸 OCR
- ✅ Сканування всього екрана
- 🌍 Підтримка мов: `eng` + `ukr` + `rus`

### 🤖 AI (Gemini 2.5 Pro)
- ✅ Визначення правильної відповіді: `a`, `b`, `c`
- ✅ Підтримка кількох відповідей: `[a,b,f]`
- ✅ Повернення чистого коду без коментарів
- ✅ Коректний розбір тестів і скриптів

### 🎛 Гарячі клавіші

| Клавіша | Дія |
|---------|----------|
| `Z` | OCR + надсилання в AI |
| `X` | Наступний варіант відповіді |
| `C` | Перемикання типу іконки |
| `V` | Скопіювати текстову відповідь |

### 🖥 Іконка в треї
- ✅ Показ літер відповіді
- ✅ Власна іконка (`img.png`)
- ✅ Прозорий режим

### 🧰 Меню трея
- 🔒 **Lock Hotkeys** — блокування Z/X/C/V
- ❌ **Exit** — вихід

### ⏳ Анімація «AI думає»
Показується спеціальною міні-анімацією в треї.

---

## 📁 Структура проєкту
```
AI-OCR-Tray-Bot/
│
├── config.py           ← усі налаштування
├── Mac.pyw             ← версія для macOS
├── win.pyw             ← версія для Windows
├── img.png             ← іконка (необов'язково)
└── README.md           ← документація
```

---

## ⚙️ Налаштування (config.py)
```python
# API KEY
API_KEY = "your-api-key"

# Версія моделі Gemini
GEMINI_MODEL = "gemini-2.5-pro"

# Мови OCR
OCR_LANG = "eng+ukr+rus"

# Шлях до OCR-рушія (Tesseract)
# Windows — обов'язковий
# macOS — можна залишити порожнім
TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Шлях до іконки трея
ICON_PATH = "img.png"

# Гарячі клавіші
HOTKEY_OCR = "z"
HOTKEY_NEXT = "x"
HOTKEY_MODE = "c"
HOTKEY_COPY = "v"
```

---

## 🍏 Встановлення на macOS

### 1️⃣ Встановити Homebrew (якщо немає)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2️⃣ Встановити Tesseract OCR
```bash
brew install tesseract
```

### 3️⃣ Встановити залежності
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pillow pytesseract mss pynput pystray google-genai pyperclip
```

### 4️⃣ Запуск
```bash
python3 Mac.pyw
```

---

## 🪟 Встановлення на Windows

### 1️⃣ Встановити Tesseract OCR

Офіційний інсталятор:

📥 [tesseract-ocr-w64-setup-5.5.0.20241111.exe](https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe)

Шлях після встановлення зазвичай:
```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

⚠️ Пропиши його в `config.py` → `TESSERACT_PATH`

### 2️⃣ Створити віртуальне середовище
```cmd
py -m venv .venv
.venv\Scripts\activate
```

### 3️⃣ Встановити бібліотеки
```cmd
pip install pillow pytesseract mss pynput pystray google-genai pyperclip
```

### 4️⃣ Запуск
```cmd
python win.pyw
```

---

## 🎹 Керування

| Дія | Клавіша |
|----------|---------|
| **OCR + AI** | `Z` |
| **Наступна відповідь** | `X` |
| **Перемкнути іконку** | `C` |
| **Скопіювати текст/код** | `V` |
| **Заблокувати клавіші** | 🖱 Трей → Lock Hotkeys |
| **Закрити програму** | 🖱 Трей → Exit |

---