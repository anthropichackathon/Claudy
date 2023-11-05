import threading
import tkinter as tk

import pyperclip
from pynput import keyboard

from src.logger.basic_logger import Logger
from src.processors.decision_maker import run as run_decision_maker
from src.processors.first_round import run as run_bio
from src.utils.tags import get_tag_content


def bio_function(input_val):
    run_bio(input_val)


def new_window_function():
    new_window = tk.Toplevel(root)
    new_window.geometry("480x480")

    new_input_text = tk.Text(new_window)
    new_input_text.pack(expand=True, fill=tk.BOTH)

    new_input_text.focus_set()

    def on_enter(event):
        new_output_text = tk.Text(new_window)
        new_output_text.pack()
        new_output_text.insert(tk.END, "Thinking...\n")

        thread = threading.Thread(target=bio_function, args=(new_input_text.get("1.0", "end-1c"),))
        thread.start()

        new_window.after(5000, new_window.destroy)

    new_input_text.bind('<Return>', on_enter)


root = tk.Tk()
w = 800
h = 480
root.geometry(f"{w}x{h}")

root.withdraw()

output_text = tk.Text(root, state=tk.DISABLED)
output_text.grid(row=0, column=0, sticky='nsew')

input_text = tk.Entry(root)
input_text.grid(row=1, column=0, sticky='nsew')

log_text = tk.Text(root, state='disabled')
log_text.grid(row=0, column=1, rowspan=2, sticky='nsew')

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="BIO", menu=file_menu)

file_menu.add_command(label="Tell me about yourself", command=new_window_function)


def backend_function(event):
    input_val = input_text.get().strip()
    output = f"User: {input_val}\n"
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, output + '\n')
    output_text.insert(tk.END, "Thinking...\n")
    output_text.config(state=tk.DISABLED)
    input_text.delete(0, 'end')
    thread = threading.Thread(target=run_function, args=(input_val, logger))
    thread.start()


def run_function(input_val, logger):
    res = get_tag_content(run_decision_maker(input_val, logger.logger), "response")
    if not res:
        res = "New info saved to memory"
    assistant_response = "\nAssistant: " + res
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"User: {input_val}\n")
    output_text.insert(tk.END, assistant_response + '\n')
    output_text.config(state=tk.DISABLED)


current_keys = set()


def toggle_app_window():
    if root.state() in ['withdrawn', 'iconic']:
        root.deiconify()
    else:
        root.withdraw()
    current_keys.clear()


def paste_from_clipboard():
    if root.state() in ['withdrawn', 'iconic']:
        root.deiconify()
    root.after(100, lambda: input_text.focus_force())
    input_text.delete(0, tk.END)
    input_text.insert(tk.END, pyperclip.paste())
    backend_function(None)
    current_keys.clear()


COMBINATIONS = {
    frozenset([keyboard.Key.shift, keyboard.Key.alt_l, keyboard.KeyCode.from_char('t')]): toggle_app_window,
    frozenset([keyboard.Key.shift, keyboard.Key.alt_l, keyboard.KeyCode.from_char('v')]): paste_from_clipboard
}


def on_press(key):
    current_keys.add(key)
    if frozenset(current_keys) in COMBINATIONS:
        COMBINATIONS[frozenset(current_keys)]()


def on_release(key):
    try:
        current_keys.remove(key)
    except KeyError:
        pass


listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

input_text.focus_set()
input_text.bind('<Return>', backend_function)

logger = Logger(log_text)

# This is the new line to intercept the "X" button
root.protocol("WM_DELETE_WINDOW", toggle_app_window)
root.mainloop()
