import threading
import tkinter as tk


def background_task():
    # This is where you put any task that you want to run in the background
    raise NotImplementedError('This is where you put any task that you want to run in the background')
    while True:
        pass


def start_background_task():
    thread = threading.Thread(target=background_task)
    thread.start()


# Create the main window
root = tk.Tk()

# Create a button that will start the background task when clicked
start_button = tk.Button(root, text='Start', command=start_background_task)
start_button.pack()

# Run the GUI
root.mainloop()
