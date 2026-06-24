# ----------------------------
# ФАЙЛ КОНФІГУРАЦІЇ (Gemini + Groq)
# ----------------------------

# Ключі обох провайдерів
GEMINI_API_KEY = "KEY"
GROQ_API_KEY   = "KEY"

# Між ними програма перемикається за завантаженістю (хто менш "шумний" — той першим).
# Пул моделей. Програма перемикається між ними за завантаженістю ("шумністю"):
# на старті пробує згори вниз, далі сама пріоритезує ту, що відповідає швидше.
# Порядок: від найрозумніших до найлегших, провайдери чергуються.
BACKENDS = [
    # --- ТОП: найрозумніші ---
    {"provider": "gemini", "model": "gemini-3.5-flash"},        # найновіша Gemini
    {"provider": "groq",   "model": "llama-3.3-70b-versatile"}, # найбільша Groq (70B)
    {"provider": "groq",   "model": "openai/gpt-oss-120b"},
    {"provider": "groq",   "model": "qwen/qwen3-32b"},
    # --- СЕРЕДНІ: швидкі й точні ---
    {"provider": "gemini", "model": "gemini-2.5-flash"},
    {"provider": "groq",   "model": "llama-3.1-8b-instant"},

    # --- ЛЕГКІ: запасні, найшвидші ---
   {"provider": "gemini", "model": "gemini-2.5-flash-lite"},
   {"provider": "groq",   "model": "gemma2-9b-it"},
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
