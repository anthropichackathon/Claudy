import tkinter as tk


class StartButton(tk.Button):
    def __init__(self, master=None, key_listener=None, stop_button=None, **kwargs):
        super().__init__(master, text='Start', command=self.start_key_listener, **kwargs)
        self.key_listener = key_listener
        self.stop_button = stop_button

    def start_key_listener(self):
        self.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.key_listener.start()
