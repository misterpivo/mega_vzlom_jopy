import pytesseract
import mss
from PIL import Image, ImageDraw, ImageFont
from pynput import keyboard
from google import genai
from google.genai import errors
import threading
import time
import random
import pystray
from pystray import MenuItem
import pyperclip
import re
import os
import sys

# ---------------------------
# CONFIG IMPORT
# ---------------------------
import config


# ---------------------------
# SETUP TESSERACT (WINDOWS)
# ---------------------------
# Шлях із config.py
if config.TESSERACT_PATH.strip():
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH


# ---------------------------
# SYSTEM PROMPT
# ---------------------------
SYSTEM_PROMPT = """
1)Якщо тобі надіслали питання з варіантами відповідей (a, b, c, d, e, f):
Якщо правильна одна — відповідай лише літерою, наприклад: c
Якщо правильних декілька — відповідай строго у вигляді списку: [a,b,f]
ЖОДНИХ інших символів, слів, пояснень.

2)Якщо потрібно повернути текст/скрипт/код (SQL, C, Python тощо):
Відповідай ЛИШЕ чистим кодом або текстом, БЕЗ коментарів.
Жодних рядків з коментарями (#, //, /* */ тощо).
Жодних пояснень словами
"""


# ---------------------------
# INIT GEMINI
# ---------------------------
client = genai.Client(api_key=config.API_KEY)
history = [SYSTEM_PROMPT]


# ---------------------------
# GLOBAL STATE
# ---------------------------
tray_icon = None
answer_list = []
answer_index = 0
icon_mode = 0
is_thinking = False
thinking_thread = None
last_text_answer = ""
hotkeys_enabled = True

CHOICE_LETTERS = set("abcdef")


# ---------------------------
# LOAD ICON
# ---------------------------
try:
    custom_image = Image.open(config.ICON_PATH).convert("RGBA")
except:
    print(f"⚠ ICON NOT FOUND: {config.ICON_PATH}")
    custom_image = None


# ---------------------------
# HELPERS
# ---------------------------
def is_choice_answer(text: str) -> bool:
    t = text.strip()

    if len(t) == 1 and t.lower() in CHOICE_LETTERS:
        return True

    # варіанти у вигляді [a,b,c]
    if t.startswith("[") and t.endswith("]"):
        t = t[1:-1]

    parts = [p.strip().lower() for p in t.split(",") if p.strip()]
    return len(parts) > 0 and all(len(p) == 1 and p in CHOICE_LETTERS for p in parts)


def extract_choices(text: str):
    t = text.strip()
    if t.startswith("[") and t.endswith("]"):
        t = t[1:-1]
    return [p.strip().lower() for p in t.split(",") if p.strip()]


# ---------------------------
# ICON RENDERING
# ---------------------------
def create_transparent_icon(letter):
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 150)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((256 - w) / 2, (256 - h) / 2), letter, fill="white", font=font)

    return img


def draw_letter_on_custom_icon(letter):
    if custom_image is None:
        return create_transparent_icon(letter)

    img = custom_image.copy()
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 150)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((img.width - w) / 2, (img.height - h) / 2),
              letter, fill="white", font=font)

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


# ---------------------------
# THINKING ANIMATION
# ---------------------------
def thinking_animation():
    global is_thinking
    frames = ["·", "··", "···", "··", "·"]
    i = 0

    while is_thinking:
        tray_update_icon(frames[i])
        i = (i + 1) % len(frames)
        time.sleep(0.25)


# ---------------------------
# OCR
# ---------------------------
def ocr_screenshot():
    with mss.MSS() as sct:
        monitor = sct.monitors[1]  # основний екран
        screenshot = sct.grab(monitor)

    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
    return pytesseract.image_to_string(img, lang=config.OCR_LANG).strip()


# ---------------------------
# GEMINI REQUEST (з повторами + запасними моделями)
# ---------------------------
def ask_gemini(question, max_retries=4):
    history.append(f"User: {question}")

    # основна модель з config + запасні на випадок 503/перевантаження
    candidates = [config.GEMINI_MODEL, "gemini-3.5-flash", "gemini-2.5-pro", "gemini-2.5-flash"]
    models_to_try = []
    for m in candidates:                 # прибираємо дублікати, зберігаючи порядок
        if m and m not in models_to_try:
            models_to_try.append(m)

    last_error = None
    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents="\n".join(history)
                )
                ans = response.text.strip()
                history.append(f"Assistant: {ans}")
                return ans

            except errors.ServerError as e:
                # 503/500 — сервер перевантажений, чекаємо і пробуємо ще
                last_error = e
                wait = (2 ** attempt) + random.uniform(0, 1)  # 1с → 2с → 4с → 8с + джиттер
                print(f"⏳ {model_name}: сервер зайнятий ({getattr(e, 'code', '?')}), повтор через {wait:.1f}с...")
                time.sleep(wait)

            except errors.ClientError as e:
                # 400/403/404 — ключ/модель/запит, повтори не допоможуть
                history.pop()
                msg = f"❌ Помилка запиту: {e}"
                print(msg)
                return msg

        print(f"⚠ Модель {model_name} недоступна, пробую наступну...")

    history.pop()
    msg = f"❌ Усі моделі недоступні. Остання помилка: {last_error}"
    print(msg)
    return msg


# ---------------------------
# HOTKEY ACTIONS
# ---------------------------
def process_z_key():
    global answer_list, answer_index, is_thinking, last_text_answer

    text = ocr_screenshot()

    is_thinking = True
    threading.Thread(target=thinking_animation).start()

    ai_answer = ask_gemini(text)

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


# ---------------------------
# HOTKEY LISTENER
# ---------------------------
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


# ---------------------------
# TRAY MENU
# ---------------------------
def lock_hotkeys(icon, item):
    global hotkeys_enabled, icon_mode

    hotkeys_enabled = not hotkeys_enabled

    if not hotkeys_enabled:
        icon_mode = 1
        tray_update_icon(answer_list[answer_index] if answer_list else "?")
    else:
        icon_mode = 0
        tray_update_icon(answer_list[answer_index] if answer_list else "?")


def exit_app(icon, item):
    icon.stop()
    os._exit(0)


# ---------------------------
# MAIN
# ---------------------------
def main():
    global tray_icon

    tray_menu = pystray.Menu(
        MenuItem("🔒 Lock hotkeys", lock_hotkeys),
        MenuItem("❌ Exit", exit_app)
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