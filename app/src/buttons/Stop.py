import tkinter as tk


class StopButton(tk.Button):
    def __init__(self, master=None, key_listener=None, start_button=None, **kwargs):
        super().__init__(master, text='Stop', state=tk.DISABLED, command=self.stop_key_listener, **kwargs)
        self.key_listener = key_listener
        self.start_button = start_button

    def stop_key_listener(self):
        self.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.key_listener.stop()
