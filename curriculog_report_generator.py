import tkinter as tk
import os
import configparser
from classes import report_generator


# Create the main window
window = tk.Tk()
window.title("Curriculog Report Generator")
# Create a frame to hold the title and buttons
main_frame = tk.Frame(window)
main_frame.pack(padx=10, pady=10)

# Create the title label
title_label = tk.Label(main_frame, text="Curriculog Report Generator", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

# Create a frame to hold the buttons
button_frame = tk.Frame(window)
button_frame.pack(padx=10, pady=10)
# Create the buttons
new_report_button = tk.Button(button_frame, text="New Report", command=new_report)
new_report_button.grid(row=0, column=0, padx=10, pady=10)

update_report_button = tk.Button(button_frame, text="Update Existing Report")
update_report_button.grid(row=0, column=1, padx=10, pady=10)

restore_previous_report_button = tk.Button(button_frame, text="Restore Previous Report", command=new_report)
restore_previous_report_button.grid(row=0, column=2, padx=10, pady=10)

# Start the main loop
window.mainloop()