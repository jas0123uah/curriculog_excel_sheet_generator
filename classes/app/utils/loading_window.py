import tkinter as tk
import sys
class LoadingWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Loading...")
        self.window.geometry("300x200")
        self.textbox = tk.Text(self.window)
        self.textbox.pack()
        sys.stdout.write = self.redirector
    def redirector(self, inputStr):
        if len(inputStr) > 0:
            self.textbox.insert(tk.INSERT, inputStr)
            self.textbox.see(tk.END)
            self.textbox.update()
    def destroy(self):
        sys.stdout.write = sys.__stdout__
        self.window.destroy()
