import tkinter as tk
import pyperclip
from pynput import keyboard

# Create the main window
root = tk.Tk()
root.title("Background App")
root.geometry("480x320")  # Set the size of the window


# Function to toggle the app window
def toggle_app_window():
    if root.state() == 'withdrawn':
        root.deiconify()  # Show the window
    else:
        root.withdraw()  # Hide the window


# Function to paste clipboard content into the input_text
def paste_from_clipboard():
    if root.state() == 'withdrawn':
        root.deiconify()  # Ensure the window is visible
    root.after(100, lambda: input_text.focus_force())  # Focus the input text after the window is visible
    input_text.delete(0, tk.END)  # Clear the current content
    input_text.insert(tk.END, pyperclip.paste())  # Paste clipboard content
    process_input(input_text.get())  # Process the pasted text


# Set the root window to withdraw to start with
root.withdraw()

# Cloud Input Display
cloud_input_display = tk.Label(root, text="", anchor="nw", justify=tk.LEFT)
cloud_input_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Response Display
response_display = tk.Label(root, text="", anchor="sw", justify=tk.LEFT)
response_display.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Entry for text input
input_text = tk.Entry(root)
input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


# Send button action
def on_send_button():
    input_value = input_text.get()
    process_input(input_value)


# Send button (functionalities to be defined by the user)
send_button = tk.Button(root, text='Send', command=on_send_button)
send_button.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


# Function to process the input and display the response
def process_input(input_value):
    # Display the input value in the cloud input display
    cloud_input_display.config(text=f"Cloud Input: {input_value}")

    # Placeholder for processing the input and generating a response
    response = f"Processed response for: {input_value}"

    # Display the response in the response display
    response_display.config(text=f"Response: {response}")


# The key combination to check
COMBINATIONS = {
    frozenset([keyboard.Key.shift, keyboard.Key.alt_l, keyboard.KeyCode.from_char('t')]): toggle_app_window,
    frozenset([keyboard.Key.shift, keyboard.Key.alt_l, keyboard.KeyCode.from_char('v')]): paste_from_clipboard
}

# The currently active keys
current_keys = set()


def on_press(key):
    current_keys.add(key)
    if frozenset(current_keys) in COMBINATIONS:
        COMBINATIONS[frozenset(current_keys)]()


def on_release(key):
    try:
        current_keys.remove(key)
    except KeyError:
        pass  # Key was not in the set


# Listener to check for hotkey presses
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

root.mainloop()

