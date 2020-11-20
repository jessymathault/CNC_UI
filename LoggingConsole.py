
import logging
import tkinter as tk


class LoggingConsole(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.setLevel(logging.INFO)
        self.widget = widget
        self.widget.config(state='disabled')

    def emit(self, record):
        self.widget.config(state='normal')
        self.widget.insert(tk.END, self.format(record) + '\n')
        self.widget.see(tk.END)
        self.widget.config(state='disabled')