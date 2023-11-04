import tkinter as tk

from dotenv import load_dotenv

from app.src.KeyListener import KeyListener

load_dotenv()


def start_key_listener():
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    key_listener.start()


def stop_key_listener():
    stop_button.config(state=tk.DISABLED)
    start_button.config(state=tk.NORMAL)
    key_listener.stop()


def on_close():
    key_listener.stop()
    root.destroy()


# Create the main window
root = tk.Tk()
w = 480
h = 320
root.geometry(f"{w}x{h}")
root.protocol("WM_DELETE_WINDOW", on_close)

# Create the Text widget for logs
log_text = tk.Text(root)
log_text.grid(row=0, column=0, columnspan=2, sticky='nsew')

# Create a key listener
key_listener = KeyListener(log_text)

# Create the start and stop buttons
start_button = tk.Button(root, text='Start', command=start_key_listener)
start_button.grid(row=1, column=0, sticky='nsew')

stop_button = tk.Button(root, text='Stop', state=tk.DISABLED, command=stop_key_listener)
stop_button.grid(row=1, column=1, sticky='nsew')

root.grid_rowconfigure(0, weight=1)  # make the Text widget expandable
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Run the GUI
root.mainloop()
