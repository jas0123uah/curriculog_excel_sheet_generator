import tkinter as tk
import os
import configparser
#import classes.report_generator
from curriculog_excel_sheet_generator.classes import ReportGenerator
#from .report_generator import ReportGenerator
#from ..report_generator import ReportGenerator
from curriculog_excel_sheet_generator.classes.app.windows.starting_frame import build_starting_frame


# Create the main window
window = tk.Tk()
window.title("Curriculog Report Generator")
# Create a frame to hold the title and buttons
build_starting_frame(window)


# Start the main loop
window.mainloop()