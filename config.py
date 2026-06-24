# ----------------------------
# ФАЙЛ КОНФІГУРАЦІЇ (Gemini + Groq)
# ----------------------------

# Ключі обох провайдерів
GEMINI_API_KEY = "KEY"
GROQ_API_KEY   = "KEY"

# Розумна версія моделі кожного провайдера.
# Між ними програма перемикається за завантаженістю (хто менш "шумний" — той першим).
BACKENDS = [
    {"provider": "gemini", "model": "gemini-3.5-flash"},
    {"provider": "groq",   "model": "llama-3.3-70b-versatile"},
]

# Мови OCR
OCR_LANG = "eng+ukr+rus"

# Шлях до OCR-рушія (Tesseract)
TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Шлях до іконки
ICON_PATH = "img.png"

# ГАРЯЧІ КЛАВІШІ
HOTKEY_OCR = "z"
HOTKEY_NEXT = "x"
HOTKEY_MODE = "c"
HOTKEY_COPY = "v"
