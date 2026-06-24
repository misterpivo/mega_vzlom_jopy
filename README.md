---

## ⚙️ Налаштування (config.py)
```python
# Ключі обох провайдерів
GEMINI_API_KEY = "your-gemini-key"
GROQ_API_KEY   = "your-groq-key"

# Пул моделей. Перемикання за завантаженістю.
# Порядок: від найрозумніших до найлегших, провайдери чергуються.
BACKENDS = [
    {"provider": "gemini", "model": "gemini-3.5-flash"},
    {"provider": "groq",   "model": "llama-3.3-70b-versatile"},
    {"provider": "gemini", "model": "gemini-2.5-flash"},
    {"provider": "groq",   "model": "llama-3.1-8b-instant"},
    {"provider": "gemini", "model": "gemini-2.5-flash-lite"},
    {"provider": "groq",   "model": "gemma2-9b-it"},
]

# Мови OCR
OCR_LANG = "eng+ukr+rus"

# Шлях до Tesseract (Windows — обов'язковий, macOS — можна "")
TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Іконка
ICON_PATH = "img.png"

# Гарячі клавіші
HOTKEY_OCR = "z"
HOTKEY_NEXT = "x"
HOTKEY_MODE = "c"
HOTKEY_COPY = "v"
```

---

## 🍏 Встановлення на macOS

```bash
# 1. Homebrew (якщо немає)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Tesseract OCR
brew install tesseract

# 3. Залежності
python3 -m venv .venv
source .venv/bin/activate
pip install pillow pytesseract mss pynput pystray google-genai groq pyperclip

# 4. Запуск
python3 Mac.pyw
```

---

## 🪟 Встановлення на Windows

### 1️⃣ Tesseract OCR
Офіційний інсталятор:
📥 [tesseract-ocr-w64-setup-5.5.0.20241111.exe](https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe)

Шлях зазвичай `C:\Program Files\Tesseract-OCR\tesseract.exe` — пропиши його в `config.py` → `TESSERACT_PATH`.

### 2️⃣ Середовище й бібліотеки
```cmd
py -m venv .venv
.venv\Scripts\activate
pip install pillow pytesseract mss pynput pystray google-genai groq pyperclip
```

### 3️⃣ Запуск
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