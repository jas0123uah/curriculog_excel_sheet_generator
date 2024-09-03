import tkinter as tk
from classes.app.windows.starting_frame import build_starting_frame

# Create the main window
window = tk.Tk()
window.title("Curriculog Report Generator")
# Create a frame to hold the title and buttons
build_starting_frame(window)


# Start the main loop
window.mainloop()