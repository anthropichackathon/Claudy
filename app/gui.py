import threading
import tkinter as tk

from src.processors.decision_maker import run
from src.utils.tags import get_tag_content

root = tk.Tk()
w = 480
h = 480  # Increase the height of the window
root.geometry(f"{w}x{h}")

output_text = tk.Text(root, state=tk.DISABLED)
output_text.grid(row=3, column=0, sticky='nsew')  # Adjust the position of the output_text widget

input_text = tk.Entry(root)
input_text.grid(row=4, column=0, sticky='nsew')  # Adjust the position of the input_text widget

root.grid_rowconfigure(3, weight=1)  # Add this line
root.grid_rowconfigure(4, weight=1)  # Add this line
root.grid_columnconfigure(0, weight=1)  # Add this line

input_text.focus_set()  # Set the focus to the input_text widget


def backend_function(event):
    # This is your backend function
    input_val = input_text.get().strip()
    output = f"User: {input_val}\n"
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, output + '\n')
    output_text.insert(tk.END, "Thinking...\n")
    output_text.config(state=tk.DISABLED)
    input_text.delete(0, 'end')
    # use threading to handle the time-consuming function
    thread = threading.Thread(target=run_function, args=(input_val,))
    thread.start()


def run_function(input_val):
    res = get_tag_content(run(input_val), "response")
    assistant_response = "Assistant: " + res
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"User: {input_val}\n")
    output_text.insert(tk.END, assistant_response + '\n')
    output_text.config(state=tk.DISABLED)


input_text.bind('<Return>', backend_function)

root.mainloop()
