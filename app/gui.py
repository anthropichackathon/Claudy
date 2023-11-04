import tkinter as tk

from dotenv import load_dotenv

from app.src.KeyListener import KeyListener
from app.src.buttons.Start import StartButton
from app.src.buttons.Stop import StopButton

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
log_text.grid(row=0, column=0, rowspan=6, sticky='nsew')

# Create a key listener
key_listener = KeyListener(log_text)

# Create the start button first without griding it
start_button = StartButton(root, key_listener=key_listener)

# Then create the stop button and pass the start button to it
stop_button = StopButton(root, key_listener=key_listener, start_button=start_button)
stop_button.grid(row=0, column=2, sticky='new')

# Now grid the start button and pass the stop button to it
start_button.stop_button = stop_button
start_button.grid(row=0, column=1, sticky='new')

# Create more buttons
button2 = tk.Button(root, text='Daily summary')
button2.grid(row=1, column=1, sticky='nsew', columnspan=2)

button3 = tk.Button(root, text='Consolidate knowledge')
button3.grid(row=2, column=1, sticky='nsew', columnspan=2)

button4 = tk.Button(root, text='Help me')
button4.grid(row=3, column=1, sticky='nsew', columnspan=2)

button5 = tk.Button(root, text='Voice')
button5.grid(row=4, column=1, sticky='sew')

button6 = tk.Button(root, text='Snip')
button6.grid(row=4, column=2, sticky='sew')

# Create input for text
input_text = tk.Entry(root)
input_text.grid(row=5, column=0, sticky='nsew')

# Create button for inputting image
input_button = tk.Button(root, text='Input Image')
input_button.grid(row=5, column=1, columnspan=2, sticky='ew')

root.grid_rowconfigure(0, weight=1)  # make the Text widget expandable
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)
root.grid_columnconfigure(2, weight=0)

# Run the GUI
root.mainloop()
