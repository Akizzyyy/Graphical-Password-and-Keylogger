import os
import time
import json
import torch
import threading
import numpy as np
import pyautogui
import pytesseract
import tkinter as tk
import torch.nn as nn
import torchvision.transforms as transforms
from tkinter import ttk
from PIL import Image
from pynput import mouse
from collections import Counter

# ---- CONFIG ----
JSON_PATH = r"C:\Users\tayo6\Downloads\Password Project\graphical-password-backend\observations\james_emoji_login.json"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
IMG_SIZE = 256
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL_PATH_WHEEL = "model_wheel.pth"
MODEL_PATH_EMOJI = "model_emoji.pth"

# ---- STATIC DATA ----
RING_COLORS = [
    ["red", "green", "blue", "yellow", "purple", "orange"],
    ["cyan", "magenta", "lime", "pink", "gray", "brown"],
    ["gold", "silver", "navy", "teal", "maroon", "olive"]
]
BOTTOM_RIGHT_COORDS = [(1104, 680), (1062, 651), (1014, 623)]
EMOJI_LABELS = [
    "😀", "😎", "🐱", "🐶", "😡", "👽", "😺", "🤖", "💩", "👻",
    "🦄", "🐸", "🐵", "🦊", "🐷", "🐼", "🐙", "🧠", "👁️", "👅",
    "🦷", "🧛", "🧟", "🦸", "🧞"
]
COLOR_RGB_MAP = {
    "red": (255, 0, 0), "green": (0, 128, 0), "blue": (0, 0, 255),
    "yellow": (255, 255, 0), "purple": (128, 0, 128), "orange": (255, 165, 0),
    "cyan": (0, 255, 255), "magenta": (255, 0, 255), "lime": (0, 255, 0),
    "pink": (255, 192, 203), "gray": (128, 128, 128), "brown": (139, 69, 19),
    "gold": (255, 215, 0), "silver": (192, 192, 192), "navy": (0, 0, 128),
    "teal": (0, 128, 128), "maroon": (128, 0, 0), "olive": (128, 128, 0)
}
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor()
])

class VisualEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d((1, 1))
        )
        self.fc = nn.Linear(128, 128)

    def forward(self, x):
        return self.fc(self.encoder(x).view(x.size(0), -1))

class PasswordDecoder(nn.Module):
    def __init__(self, output_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, output_dim)
        )

    def forward(self, x):
        return self.fc(x)

class PasswordLearner(nn.Module):
    def __init__(self, output_dim):
        super().__init__()
        self.encoder = VisualEncoder()
        self.decoder = PasswordDecoder(output_dim)

    def forward(self, x):
        return self.decoder(self.encoder(x))

def capture_screen():
    screenshot = pyautogui.screenshot()
    return transform(screenshot.resize((IMG_SIZE, IMG_SIZE)).convert("RGB")), screenshot

def closest_color(rgb):
    return min(COLOR_RGB_MAP.items(), key=lambda item: np.linalg.norm(np.array(item[1]) - np.array(rgb)))[0]

def guess_to_colors(guess):
    return [RING_COLORS[i][g] for i, g in enumerate(guess)]

def predict_password(model, mode):
    x, _ = capture_screen()
    x_tensor = x.unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        pred = model(x_tensor)
        if mode == "wheel":
            guess = pred.view(3, 6).argmax(dim=1).tolist()
            return guess_to_colors(guess)
        else:
            idx = pred.argmax(dim=1).item()
            return EMOJI_LABELS[idx]

def detect_login_click():
    def on_click(x, y, button, pressed):
        if pressed:
            width, height = pyautogui.size()
            if width * 0.45 < x < width * 0.55 and height * 0.7 < y < height * 0.85:
                return False
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    return True

def detect_login_success():
    time.sleep(1.0)
    try:
        text = pytesseract.image_to_string(pyautogui.screenshot()).lower()
    except Exception:
        return False
    return any(success_msg in text for success_msg in [
        "login successful", "return to home", "registration successful"
    ])

def start_gui():
    root = tk.Tk()
    root.title("Shoulder Surfer AI")
    root.geometry("800x600")

    mode_var = tk.StringVar(value="wheel")
    status = tk.StringVar()
    log_box = tk.Text(root, height=20)

    def log(msg):
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)

    stop_flag = threading.Event()

    def start_watching():
        stop_flag.clear()
        model_path = MODEL_PATH_WHEEL if mode_var.get() == "wheel" else MODEL_PATH_EMOJI
        out_dim = 18 if mode_var.get() == "wheel" else 25
        model = PasswordLearner(output_dim=out_dim).to(DEVICE)

        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=DEVICE))

        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        loss_fn = nn.CrossEntropyLoss()

        def loop():
            attempts, successes = 0, 0
            seen_emojis = []
            while not stop_flag.is_set():
                log("[🕵️] Watching for login attempt...")
                detect_login_click()
                x, screenshot = capture_screen()
                x_tensor = x.unsqueeze(0).to(DEVICE)
                success = detect_login_success()

                if success:
                    if mode_var.get() == "wheel":
                        true_colors = [closest_color(screenshot.getpixel(coord)) for coord in BOTTOM_RIGHT_COORDS]
                        label = [RING_COLORS[i].index(c) for i, c in enumerate(true_colors)]
                        pred = model(x_tensor)
                        target = torch.tensor(label).to(DEVICE)
                        loss = sum([loss_fn(pred[:, i*6:(i+1)*6], target[i].unsqueeze(0)) for i in range(3)])
                        log(f"[🎯] True colors: {true_colors}")
                    else:
                        try:
                            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                grid = data["grid"]
                                row = data["row"]
                                col = data["col"]
                                clicked_emoji = data["clickedEmoji"]
                                row_emojis = grid[row]
                                col_emojis = [grid[r][col] for r in range(5)]
                        except Exception as e:
                            log(f"[⚠️] Failed to read emoji login data: {e}")
                            continue

                        log("\n[📊] Emoji Grid Layout:")
                        for r in grid:
                            log("  ".join(r))
                        log(f"\n[👁️] Clicked Emoji: '{clicked_emoji}' at Row {row}, Column {col}")
                        log(f"[➡️] Row {row}: {row_emojis}")
                        log(f"[⬇️] Column {col}: {col_emojis}")

                        seen_emojis.append(row_emojis + col_emojis)

                        if len(seen_emojis) > 1:
                            flat = [e for trial in seen_emojis for e in trial]
                            counter = Counter(flat)
                            recurring = {k: v for k, v in counter.items() if v >= 2}
                            most_common = counter.most_common(2)

                            log("\n[📚] Learned Candidate Emojis:")
                            for emoji, count in recurring.items():
                                log(f" - '{emoji}' appeared {count} times")

                            if most_common:
                                candidates = [f"{emoji} ({count})" for emoji, count in most_common]
                                log(f"\n[🎯] 🔐 Potential Password Emojis: {', '.join(candidates)}")

                            seen_emojis = [[e for e in trial if e in recurring] for trial in seen_emojis]


                        target = torch.tensor([EMOJI_LABELS.index(clicked_emoji)]).to(DEVICE)
                        pred = model(x_tensor)
                        loss = loss_fn(pred, target)

                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    torch.save(model.state_dict(), model_path)
                    successes += 1
                    log(f"[✅] Trained on password | Loss: {loss.item():.4f}")
                else:
                    guess = predict_password(model, mode_var.get())
                    log(f"[❌] Login failed — Model guessed: {guess}")
                attempts += 1
                status.set(f"Mode: {mode_var.get().upper()} | Attempts: {attempts} | Successes: {successes}")
            log("[🛑] Watching stopped.")

        threading.Thread(target=loop, daemon=True).start()

    def stop():
        stop_flag.set()

    def manual_predict():
        model_path = MODEL_PATH_WHEEL if mode_var.get() == "wheel" else MODEL_PATH_EMOJI
        out_dim = 18 if mode_var.get() == "wheel" else 25
        model = PasswordLearner(output_dim=out_dim).to(DEVICE)
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=DEVICE))
        model.eval()
        prediction = predict_password(model, mode_var.get())
        log(f"[🔮] Predicted password: {prediction}")

    ttk.Label(root, text="Shoulder Surfer AI", font=("Arial", 16)).pack(pady=10)
    ttk.Radiobutton(root, text="Wheel Spin", variable=mode_var, value="wheel").pack()
    ttk.Radiobutton(root, text="Emoji Grid", variable=mode_var, value="grid").pack()
    ttk.Label(root, textvariable=status, font=("Arial", 10)).pack(pady=5)
    ttk.Button(root, text="Start Watching", command=start_watching).pack()
    ttk.Button(root, text="Predict Password", command=manual_predict).pack()
    ttk.Button(root, text="Stop", command=stop).pack()
    log_box.pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    start_gui()
