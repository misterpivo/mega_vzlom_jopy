<div align="center">

# 📘 AI OCR Tray Bot

### ✨ Умный ассистент для тестов, задач и кода — с OCR, Gemini 2.5 в системной трее
</div>

---

## 🎯 Описание

**AI OCR Tray Bot** — это лёгкая фоновая утилита для Windows и macOS, которая:

- 📸 **делает OCR всего экрана**
- 🤖 **отправляет распознанный текст в Gemini 2.5 Pro**
- 🅰 **показывает правильный вариант ответа прямо в иконке трея**
- 💻 **умеет работать с кодом и текстами**
- 📎 **позволяет копировать ответ одним нажатием**
- 🔒 **имеет блокировку горячих клавиш**
- ❌ **и завершение через меню трея**

> Программа работает в фоне, почти не нагружает систему и управляется горячими клавишами.

---

## ✨ Функционал

### 📸 OCR
- ✅ Сканирование всего экрана
- 🌍 Поддержка языков: `eng` + `ukr` + `rus`

### 🤖 AI (Gemini 2.5 Pro)
- ✅ Определение правильного ответа: `a`, `b`, `c`
- ✅ Поддержка множественных ответов: `[a,b,f]`
- ✅ Возврат чистого кода без комментариев
- ✅ Корректный разбор тестов и скриптов

### 🎛 Горячие клавиши

| Клавиша | Действие |
|---------|----------|
| `Z` | OCR + отправка в AI |
| `X` | Следующий вариант ответа |
| `C` | Переключение типа иконки |
| `V` | Скопировать текстовый ответ |

### 🖥 Иконка в трее
- ✅ Показ букв ответа
- ✅ Кастомная иконка (`img.png`)
- ✅ Прозрачный режим

### 🧰 Трей-меню
- 🔒 **Lock Hotkeys** — блокировка Z/X/C/V
- ❌ **Exit** — выход

### ⏳ Анимация «AI думает»
Показывается специальной мини-анимацией в трее.

---

## 📁 Структура проекта
```
AI-OCR-Tray-Bot/
│
├── config.py           ← все настройки
├── Mac.pyw             ← версия для macOS
├── win.pyw             ← версия для Windows
├── img.png             ← иконка (опционально)
└── README.md           ← документация
```

---

## ⚙️ Настройки (config.py)
```python
# API KEY
API_KEY = "your-api-key"

# Gemini model version
GEMINI_MODEL = "gemini-2.5-pro"

# OCR languages
OCR_LANG = "eng+ukr+rus"

# Path to custom OCR engine (Tesseract)
# Windows — обязателен
# macOS — можно оставить пустым
TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Path to tray icon
ICON_PATH = "img.png"

# Hotkeys
HOTKEY_OCR = "z"
HOTKEY_NEXT = "x"
HOTKEY_MODE = "c"
HOTKEY_COPY = "v"
```

---

## 🍏 Установка на macOS

### 1️⃣ Установить Homebrew (если нет)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2️⃣ Установить Tesseract OCR
```bash
brew install tesseract
```

### 3️⃣ Установить зависимости
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

## 🪟 Установка на Windows

### 1️⃣ Установить Tesseract OCR

Официальный инсталлятор:

📥 [tesseract-ocr-w64-setup-5.5.0.20241111.exe](https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe)

Путь после установки обычно:
```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

⚠️ Пропиши его в `config.py` → `TESSERACT_PATH`

### 2️⃣ Создать виртуальное окружение
```cmd
py -m venv .venv
.venv\Scripts\activate
```

### 3️⃣ Установить библиотеки
```cmd
pip install pillow pytesseract mss pynput pystray google-genai pyperclip
```

### 4️⃣ Запуск
```cmd
python win.pyw
```

---

## 🎹 Управление

| Действие | Клавиша |
|----------|---------|
| **OCR + AI** | `Z` |
| **Следующий ответ** | `X` |
| **Переключить иконку** | `C` |
| **Скопировать текст/код** | `V` |
| **Заблокировать клавиши** | 🖱 Трей → Lock Hotkeys |
| **Закрыть программу** | 🖱 Трей → Exit |

---
