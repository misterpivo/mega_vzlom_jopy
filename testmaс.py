import pytesseract
import mss
from PIL import Image, ImageDraw, ImageFont
from pynput import keyboard
from google import genai
from google.genai import types
from groq import Groq
import threading
import time
import random
import pystray
from pystray import MenuItem
import pyperclip
import os

import config


SYSTEM_PROMPT = """
1) Якщо тобі надіслали питання з варіантами відповідей (a, b, c, d, e, f):
Якщо правильна одна — відповідай лише літерою, наприклад: c
Якщо правильних декілька — відповідай строго у вигляді списку: [a,b,f]
Якщо треба з'єднати декілька варіантів відповідей — пиши їх послідовно (з чим з'єднувати) у вигляді списку: [b,a,f]
ЖОДНИХ інших символів, слів, пояснень.

2) Якщо потрібно повернути текст/скрипт/код (SQL, C, Python тощо):
Відповідай ЛИШЕ чистим кодом або текстом, БЕЗ коментарів.
Жодних рядків з коментарями (#, //, /* */ тощо).
Жодних пояснень словами.
"""


# ---- ІНІЦІАЛІЗАЦІЯ ПРОВАЙДЕРІВ ----
REQUEST_TIMEOUT_S = 15

gemini_client = genai.Client(
    api_key=config.GEMINI_API_KEY,
    http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_S * 1000)
)
groq_client = Groq(api_key=config.GROQ_API_KEY, timeout=float(REQUEST_TIMEOUT_S))

# нейтральна історія (user/assistant); системний промпт додається окремо під кожен провайдер
history = []


# ---- ГЛОБАЛЬНИЙ СТАН ----
tray_icon = None
answer_list = []
answer_index = 0
icon_mode = 0
is_thinking = False
last_text_answer = ""
hotkeys_enabled = True
model_switching = False

# статистика "шумності"/завантаженості кожного бекенда
backend_stats = {}  # key -> {"score": float, "fails": int}

try:
    custom_image = Image.open(config.ICON_PATH).convert("RGBA")
except:
    custom_image = None
    print(f"⚠ Іконку '{config.ICON_PATH}' НЕ знайдено!")

CHOICE_LETTERS = set("abcdef")


# ---- ОЦІНКА ЗАВАНТАЖЕНОСТІ ----
def bkey(b):
    return f"{b['provider']}:{b['model']}"


def get_score(b):
    return backend_stats.get(bkey(b), {}).get("score", 0.0)


def record_success(b, latency):
    st = backend_stats.setdefault(bkey(b), {"score": 0.0, "fails": 0})
    # EMA латентності — що швидше відповідає, то менш "шумна"
    st["score"] = 0.6 * st["score"] + 0.4 * latency
    st["fails"] = 0


def record_failure(b):
    st = backend_stats.setdefault(bkey(b), {"score": 0.0, "fails": 0})
    st["fails"] += 1
    st["score"] += 30.0  # штраф: тимчасово опускаємо в кінець черги


def order_by_noise(backends):
    # найменш завантажена (менший score) — першою
    return sorted(backends, key=get_score)


# ---- ДОПОМІЖНІ ----
def is_choice_answer(text: str) -> bool:
    t = text.strip()
    if len(t) == 1 and t.lower() in CHOICE_LETTERS:
        return True
    if t.startswith("[") and t.endswith("]"):
        inner = t[1:-1]
    else:
        inner = t
    parts = [p.strip().lower() for p in inner.split(",") if p.strip()]
    return all(len(p) == 1 and p in CHOICE_LETTERS for p in parts)


def extract_choices(text: str):
    t = text.strip()
    if t.startswith("[") and t.endswith("]"):
        t = t[1:-1]
    return [p.strip().lower() for p in t.split(",") if p.strip()]


def create_transparent_icon(letter):
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", 150)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((256 - w) / 2, (256 - h) / 2), letter, fill="white", font=font)
    return img


def draw_letter_on_custom_icon(letter):
    if custom_image is None:
        return create_transparent_icon(letter)
    img = custom_image.copy()
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", 150)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((img.width - w) / 2, (img.height - h) / 2), letter, fill="white", font=font)
    return img


def tray_update_icon(letter):
    global tray_icon, icon_mode
    if tray_icon is None:
        return
    if icon_mode == 0:
        tray_icon.icon = create_transparent_icon(letter)
    else:
        tray_icon.icon = draw_letter_on_custom_icon(letter)


def toggle_icon_mode():
    global icon_mode
    icon_mode = 1 - icon_mode
    if answer_list:
        tray_update_icon(answer_list[answer_index])
    else:
        tray_update_icon("?")


def thinking_animation():
    global is_thinking
    dots = ["·", "··", "···", "··", "·"]
    arrows = ["→", "⇒"]
    i = 0
    while is_thinking:
        if model_switching:
            tray_update_icon(arrows[i % len(arrows)])
        else:
            tray_update_icon(dots[i % len(dots)])
        i += 1
        time.sleep(0.25)


def show_switch_arrow(duration=0.6):
    global model_switching
    model_switching = True
    time.sleep(duration)
    model_switching = False


def ocr_screenshot():
    with mss.MSS() as sct:
        monitor = sct.monitors[0]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return pytesseract.image_to_string(img, lang=config.OCR_LANG).strip()


# ---- КОНВЕРТАЦІЯ ІСТОРІЇ ПІД КОЖЕН ПРОВАЙДЕР ----
def groq_messages():
    return [{"role": "system", "content": SYSTEM_PROMPT}] + history


def gemini_contents():
    lines = [SYSTEM_PROMPT]
    for m in history:
        tag = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"{tag}: {m['content']}")
    return "\n".join(lines)


# ---- ВИКЛИК БЕКЕНДА З ТАЙМАУТОМ 15с ----
def call_backend(b):
    if b["provider"] == "gemini":
        resp = gemini_client.models.generate_content(
            model=b["model"], contents=gemini_contents()
        )
        return resp.text.strip()
    else:
        resp = groq_client.chat.completions.create(
            model=b["model"], messages=groq_messages(), temperature=0
        )
        return resp.choices[0].message.content.strip()


def generate_with_timeout(b, timeout_s=REQUEST_TIMEOUT_S):
    holder = {}

    def worker():
        try:
            holder["answer"] = call_backend(b)
        except Exception as e:
            holder["error"] = e

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout_s)

    if t.is_alive():
        raise TimeoutError(f"немає відповіді за {timeout_s}с")
    if "error" in holder:
        raise holder["error"]
    return holder["answer"]


def _is_permanent(e):
    code = getattr(e, "status_code", None)
    if code is None:
        code = getattr(e, "code", None)
    return code in (400, 401, 403, 404)


def _err_label(e):
    if isinstance(e, TimeoutError):
        return "таймаут 15с"
    code = getattr(e, "status_code", None) or getattr(e, "code", None)
    return f"({code})" if code is not None else f"({type(e).__name__})"


# ---- ЗАПИТ ДО AI (2 провайдери, вибір за завантаженістю) ----
def ask_ai(question, fallback_attempts=2):
    history.append({"role": "user", "content": question})

    backends = list(config.BACKENDS)
    last_error = None

    # РАУНД 1: по 1 спробі, у порядку зростання "шумності"
    for idx, b in enumerate(order_by_noise(backends)):
        if idx > 0:
            show_switch_arrow()
        label = f"{b['provider']}/{b['model']}"
        try:
            t0 = time.time()
            answer = generate_with_timeout(b)
            record_success(b, time.time() - t0)
            history.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            last_error = e
            record_failure(b)
            print(f"⚠ {label}: {_err_label(e)} — піднімаю 'шумність', пробую наступну")

    # РАУНД 2: усі впали -> по {fallback_attempts} спроби, знову за завантаженістю
    print(f"⚠ Усі моделі недоступні. Запасний режим: по {fallback_attempts} спроби...")
    for idx, b in enumerate(order_by_noise(backends)):
        if idx > 0:
            show_switch_arrow()
        label = f"{b['provider']}/{b['model']}"
        for attempt in range(fallback_attempts):
            try:
                t0 = time.time()
                answer = generate_with_timeout(b)
                record_success(b, time.time() - t0)
                history.append({"role": "assistant", "content": answer})
                return answer
            except Exception as e:
                last_error = e
                record_failure(b)
                if _is_permanent(e):
                    print(f"⚠ {label}: помилка запиту {_err_label(e)}")
                    break
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"⏳ {label}: {_err_label(e)}, повтор через {wait:.1f}с...")
                time.sleep(wait)

    history.pop()
    return f"❌ Усі моделі недоступні. Остання помилка: {last_error}"


def process_z_key():
    global answer_list, answer_index, is_thinking, last_text_answer
    text = ocr_screenshot()
    is_thinking = True
    threading.Thread(target=thinking_animation).start()
    ai_answer = ask_ai(text)
    is_thinking = False
    time.sleep(0.1)
    if is_choice_answer(ai_answer):
        answer_list[:] = extract_choices(ai_answer)
        answer_index = 0
        tray_update_icon(answer_list[0])
        last_text_answer = ""
    else:
        last_text_answer = ai_answer
        answer_list[:] = ["?"]
        answer_index = 0
        tray_update_icon("?")


def process_x_key():
    global answer_index
    if not answer_list:
        return
    answer_index = (answer_index + 1) % len(answer_list)
    tray_update_icon(answer_list[answer_index])


def process_v_key():
    if last_text_answer.strip():
        pyperclip.copy(last_text_answer)
        print("\n📋 Скопійовано:\n", last_text_answer)


def hotkey_listener():
    global hotkeys_enabled
    def on_press(key):
        if not hotkeys_enabled:
            return
        try:
            if hasattr(key, "char") and key.char:
                c = key.char.lower()
                if c == config.HOTKEY_OCR:
                    threading.Thread(target=process_z_key).start()
                elif c == config.HOTKEY_NEXT:
                    threading.Thread(target=process_x_key).start()
                elif c == config.HOTKEY_MODE:
                    threading.Thread(target=toggle_icon_mode).start()
                elif c == config.HOTKEY_COPY:
                    threading.Thread(target=process_v_key).start()
        except:
            pass
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def lock_hotkeys(icon, item):
    global hotkeys_enabled, icon_mode
    hotkeys_enabled = not hotkeys_enabled
    if not hotkeys_enabled:
        icon_mode = 1
        tray_update_icon(answer_list[answer_index] if answer_list else "?")
        print("🔒 Гарячі клавіші ВИМКНЕНО")
    else:
        icon_mode = 0
        tray_update_icon(answer_list[answer_index] if answer_list else "?")
        print("🔓 Гарячі клавіші УВІМКНЕНО")


def exit_app(icon, item):
    print("❌ Вихід")
    icon.stop()
    os._exit(0)


def main():
    global tray_icon
    tray_menu = pystray.Menu(
        MenuItem("🔒 Заблокувати / Розблокувати", lock_hotkeys),
        MenuItem("❌ Вихід", exit_app)
    )
    tray_icon = pystray.Icon(
        "AI Answer",
        create_transparent_icon("?"),
        "AI Helper",
        menu=tray_menu
    )
    threading.Thread(target=hotkey_listener, daemon=True).start()
    tray_icon.run()


if __name__ == "__main__":
    main()