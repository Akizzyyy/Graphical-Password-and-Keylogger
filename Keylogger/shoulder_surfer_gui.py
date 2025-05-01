import os
import time
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

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
IMG_SIZE = 256
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL_PATH_WHEEL = "model_wheel.pth"
MODEL_PATH_EMOJI = "model_emoji.pth"
RING_COLORS = [
    ["red", "green", "blue", "yellow", "purple", "orange"],
    ["cyan", "magenta", "lime", "pink", "gray", "brown"],
    ["gold", "silver", "navy", "teal", "maroon", "olive"]
]
BOTTOM_RIGHT_COORDS = [
    (1104, 680),  # Outer ring
    (1062, 651),  # Middle ring
    (1014, 623)   # Inner ring
]
EMOJI_LABELS = [
    "😀", "😎", "🐱", "🐶", "😡",
    "👽", "😺", "🤖", "💩", "👻",
    "🦄", "🐸", "🐵", "🦊", "🐷",
    "🐼", "🐙", "🧠", "👁️", "👅",
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

def guess_to_emojis(guess):
    return [EMOJI_LABELS[g] for g in guess]

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
    text = pytesseract.image_to_string(pyautogui.screenshot()).lower()
    return "login successful" in text or "return to home" in text or "registration successful" in text

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
    try:
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    except RuntimeError as e:
        log(f"[⚠️] Skipping model load due to error: {str(e)}")

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.CrossEntropyLoss()
    emoji_observations = []

    def loop():
        attempts, successes = 0, 0
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
                    target = torch.tensor(label).to(DEVICE)
                    pred = model(x_tensor)
                    loss = sum([loss_fn(pred[:, i*6:(i+1)*6], target[i].unsqueeze(0)) for i in range(3)])
                else:
                    # Emoji Grid Logic
                    emoji_grid = [[EMOJI_LABELS[np.random.randint(0, 25)] for _ in range(5)] for _ in range(5)]
                    clicked_row, clicked_col = np.random.randint(0, 5), np.random.randint(0, 5)
                    clicked_value = emoji_grid[clicked_row][clicked_col]
                    row_emojis = emoji_grid[clicked_row]
                    col_emojis = [row[clicked_col] for row in emoji_grid]

                    print("\n[📊] Emoji Grid Layout:")
                    for row in emoji_grid:
                        print("  ".join(row))
                    print(f"\n[👁️] Clicked Emoji: '{clicked_value}' at Row {clicked_row}, Column {clicked_col}")
                    print(f"[➡️] Row {clicked_row}: {row_emojis}")
                    print(f"[⬇️] Column {clicked_col}: {col_emojis}")

                    emoji_observations.append({
                        'row_emojis': row_emojis,
                        'col_emojis': col_emojis
                    })

                    label = np.random.randint(0, 25)
                    pred = model(x_tensor)
                    target = torch.tensor([label]).to(DEVICE)
                    loss = loss_fn(pred, target)

                    if len(emoji_observations) >= 3:
                        from collections import Counter
                        row_counter = Counter()
                        col_counter = Counter()
                        for obs in emoji_observations:
                            row_counter.update(obs['row_emojis'])
                            col_counter.update(obs['col_emojis'])
                        total_counts = row_counter + col_counter
                        most_common = total_counts.most_common(3)
                        print("\n[🔎] Inference from Past Observations:")
                        for emoji, count in most_common:
                            print(f" - Emoji '{emoji}' appeared {count} times in clicked rows/columns.")
                        print(f"[🎯] Most likely password candidate: {most_common[0][0]}")

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                log(f"[✅] Trained on screen password | Loss: {loss.item():.4f}")
                torch.save(model.state_dict(), model_path)
                successes += 1
            else:
                guess = predict_password(model, mode_var.get())
                log(f"[❌] Failed — Guess: {guess}")

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
        try:
            if os.path.exists(model_path):
                model.load_state_dict(torch.load(model_path, map_location=DEVICE))
        except RuntimeError as e:
            log(f"[⚠️] Skipping model load due to error: {str(e)}")
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
