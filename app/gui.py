import threading
import tkinter as tk
from ttkthemes import ThemedTk

import pyperclip
from pynput import keyboard

from src.processors.decision_maker import run as run_decision_maker
from src.processors.first_round import run as run_bio
from src.utils.tags import get_tag_content


def bio_function(input_val):
    run_bio(input_val)


def new_window_function():
    new_window = tk.Toplevel(root)  # Create a new window
    new_window.geometry("480x480")  # Set the size of the new window

    new_input_text = tk.Text(new_window)
    new_input_text.pack(expand=True, fill=tk.BOTH)

    new_input_text.focus_set()

    def on_enter(event):
        # Create text widget to display "Thinking..."
        new_output_text = tk.Text(new_window)
        new_output_text.pack()
        new_output_text.insert(tk.END, "Thinking...\n")

        # Run bio function in separate thread

        thread = threading.Thread(target=bio_function, args=(new_input_text.get("1.0", "end-1c"),))
        thread.start()

        # After the function call, you can close the window
        new_window.after(5000, new_window.destroy)  # Delay the destruction of the window by 5 seconds

    new_input_text.bind('<Return>', on_enter)


root = tk.Tk()
w = 480
h = 480  # Increase the height of the window
root.geometry(f"{w}x{h}")

root.withdraw()  # Hide the window initially

output_text = tk.Text(root, state=tk.DISABLED)
output_text.grid(row=3, column=0, sticky='nsew')

input_text = tk.Entry(root)
input_text.grid(row=4, column=0, sticky='nsew')

root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(0, weight=1)

input_text.focus_set()

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create a dropdown menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="BIO", menu=file_menu)

# Add an item to the dropdown menu that calls new_window_function
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
    thread = threading.Thread(target=run_function, args=(input_val,))
    thread.start()


def run_function(input_val):
    res = get_tag_content(run_decision_maker(input_val), "response")
    assistant_response = "\nAssistant: " + res
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"User: {input_val}\n")
    output_text.insert(tk.END, assistant_response + '\n')
    output_text.config(state=tk.DISABLED)


def toggle_app_window():
    if root.state() == 'withdrawn':
        root.deiconify()
    else:
        root.withdraw()


def paste_from_clipboard():
    if root.state() == 'withdrawn':
        root.deiconify()
    root.after(100, lambda: input_text.focus_force())
    input_text.delete(0, tk.END)
    input_text.insert(tk.END, pyperclip.paste())
    backend_function(None)  # Process the pasted text


COMBINATIONS = {
    frozenset([keyboard.Key.shift, keyboard.Key.alt_l, keyboard.KeyCode.from_char('t')]): toggle_app_window,
    frozenset([keyboard.Key.shift, keyboard.Key.alt_l, keyboard.KeyCode.from_char('v')]): paste_from_clipboard
}

current_keys = set()


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

input_text.bind('<Return>', backend_function)

root.mainloop()
