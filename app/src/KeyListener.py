import tkinter as tk
from datetime import datetime

from pynput import keyboard


class KeyListener:
    def __init__(self, log_text: tk.Text):
        self.listener = None
        self.log_text = log_text

    def on_press(self, key):
        # This function will be called when a key is pressed at fmt time
        self.log_text.insert(tk.END, f"Key pressed: {key} at {datetime.now()}\n")
        self.log_text.see(tk.END)

    def start(self):
        self.log_text.insert(tk.END, "Starting key listener...\n")
        self.log_text.see(tk.END)
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def stop(self):
        self.log_text.insert(tk.END, "Stopping key listener...\n")
        self.log_text.see(tk.END)
        if self.listener:
            self.listener.stop()
            self.listener = None
