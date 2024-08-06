import tkinter as tk
from .new_report import build_new_report_window 
def build_starting_frame(main_window):
    main_frame = tk.Frame(main_window)
    main_frame.pack(padx=10, pady=10)

    # Create the title label
    title_label = tk.Label(main_frame, text="Curriculog Report Generator", font=("Helvetica", 16, "bold"))
    title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

    # Create a frame to hold the buttons
    button_frame = tk.Frame(main_window)
    button_frame.pack(padx=10, pady=10)
    # Create the buttons
    new_report_button = tk.Button(button_frame, text="New Report", command=build_new_report_window)
    new_report_button.grid(row=0, column=0, padx=10, pady=10)

    update_report_button = tk.Button(button_frame, text="Update Existing Report")
    update_report_button.grid(row=0, column=1, padx=10, pady=10)

    restore_previous_report_button = tk.Button(button_frame, text="Restore Previous Report")
    restore_previous_report_button.grid(row=0, column=2, padx=10, pady=10)