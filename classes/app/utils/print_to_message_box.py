import tkinter as tk
class PrintToMessageBox:
    def __init__(self, messagebox_widget):
        self.messagebox_widget = messagebox_widget

    def write(self, message):
        self.messagebox_widget.insert(tk.END, message)
        #self.messagebox_widget.showinfo(tk.END, message)
        self.messagebox_widget.see(tk.END)

    def flush(self):
        pass